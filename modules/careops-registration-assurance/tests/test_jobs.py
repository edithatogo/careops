"""Pure job state-machine tests. No workers, network, data, or email are started."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from registration_assurance.jobs import (  # noqa: E402
    JobConflict, create_job, claim_job, complete_job, recover_expired_lease,
)


def job(attempt_limit: int = 2) -> dict[str, object]:
    return create_job(
        job_id="test:job-1", watch_ref="test:watch-1", provider_kind="MOCK",
        due_at_utc="2026-11-13T08:00:00Z", deadline_utc="2026-11-14T08:00:00Z",
        attempt_limit=attempt_limit,
    )


def lease(start: dict[str, object] | None = None) -> dict[str, object]:
    record = job() if start is None else start
    return claim_job(record, worker_ref="test:worker", now_utc="2026-11-13T08:00:00Z",
                     lease_seconds=600, expected_version=record["version"])


class JobProtocolTests(unittest.TestCase):
    def test_new_job_is_not_a_scheduled_external_action(self) -> None:
        start = job()
        self.assertEqual(start["state"], "queued")
        self.assertEqual(start["attempts"], 0)
        self.assertEqual(start["outbox"], [])
        self.assertFalse(start["emailEnabled"])

    def test_claim_is_versioned_and_lease_bound(self) -> None:
        leased = lease()
        self.assertEqual(leased["state"], "leased")
        self.assertEqual(leased["attempts"], 1)
        self.assertEqual(leased["version"], 2)
        self.assertEqual(leased["workerRef"], "test:worker")

    def test_early_claim_and_replayed_claim_are_rejected(self) -> None:
        with self.assertRaises(JobConflict):
            claim_job(job(), worker_ref="test:worker", now_utc="2026-11-13T07:59:59Z",
                      lease_seconds=600, expected_version=1)
        with self.assertRaises(JobConflict):
            claim_job(lease(), worker_ref="test:worker", now_utc="2026-11-13T08:01:00Z",
                      lease_seconds=600, expected_version=2)

    def test_stale_version_is_rejected(self) -> None:
        with self.assertRaises(JobConflict):
            claim_job(job(), worker_ref="test:worker", now_utc="2026-11-13T08:00:00Z",
                      lease_seconds=600, expected_version=0)

    def test_one_success_emits_no_email_and_no_credentialing_write(self) -> None:
        leased = lease()
        done = complete_job(leased, worker_ref="test:worker", now_utc="2026-11-13T08:02:00Z",
                            expected_version=2, result_kind="accepted",
                            observation_id="test:observation")
        self.assertEqual(done["state"], "succeeded")
        self.assertEqual(done["outbox"], [{"eventType": "observation_ready",
                                          "observationId": "test:observation"}])
        self.assertFalse(done["emailEnabled"])
        self.assertNotIn("practitionerStatus", done)
        with self.assertRaises(JobConflict):
            complete_job(done, worker_ref="test:worker", now_utc="2026-11-13T08:03:00Z",
                         expected_version=3, result_kind="accepted",
                         observation_id="test:observation")

    def test_unknown_delivery_requires_readback_before_retry(self) -> None:
        first = lease()
        held = complete_job(first, worker_ref="test:worker", now_utc="2026-11-13T08:05:00Z",
                            expected_version=2, result_kind="unknown_delivery")
        self.assertEqual(held["state"], "needs_reconciliation")
        self.assertEqual(held["outbox"], [])
        with self.assertRaises(JobConflict):
            claim_job(held, worker_ref="test:worker", now_utc="2026-11-13T08:10:00Z",
                      lease_seconds=600, expected_version=3)

    def test_transient_failure_backoff_and_eventual_dead_letter(self) -> None:
        first = lease()
        again = complete_job(first, worker_ref="test:worker", now_utc="2026-11-13T08:01:00Z",
                             expected_version=2, result_kind="transient_failure")
        self.assertEqual(again["state"], "retry_due")
        self.assertEqual(again["nextDueUtc"], "2026-11-13T08:02:00Z")
        second = claim_job(again, worker_ref="test:worker", now_utc="2026-11-13T08:02:00Z",
                           lease_seconds=600, expected_version=3)
        finished = complete_job(second, worker_ref="test:worker", now_utc="2026-11-13T08:03:00Z",
                                expected_version=4, result_kind="transient_failure")
        self.assertEqual(finished["state"], "dead_letter")
        self.assertEqual(finished["outbox"], [])

    def test_permanent_failure_stops_retry(self) -> None:
        first = lease()
        stopped = complete_job(first, worker_ref="test:worker", now_utc="2026-11-13T08:01:00Z",
                               expected_version=2, result_kind="permanent_failure")
        self.assertEqual(stopped["state"], "blocked")
        self.assertEqual(stopped["outbox"], [])

    def test_expired_lease_does_not_assume_operation_did_not_happen(self) -> None:
        first = lease()
        unknown = recover_expired_lease(first, now_utc="2026-11-13T08:11:00Z",
                                        expected_version=2)
        self.assertEqual(unknown["state"], "needs_reconciliation")
        self.assertEqual(unknown["outbox"], [])

    def test_wrong_worker_or_deadline_cannot_commit(self) -> None:
        first = lease()
        with self.assertRaises(JobConflict):
            complete_job(first, worker_ref="test:other", now_utc="2026-11-13T08:01:00Z",
                         expected_version=2, result_kind="accepted",
                         observation_id="test:o1")
        with self.assertRaises(JobConflict):
            complete_job(first, worker_ref="test:worker", now_utc="2026-11-13T08:12:00Z",
                         expected_version=2, result_kind="accepted",
                         observation_id="test:o1")

    def test_expired_job_cannot_be_leased(self) -> None:
        with self.assertRaises(JobConflict):
            claim_job(job(), worker_ref="test:worker", now_utc="2026-11-14T08:00:00Z",
                      lease_seconds=600, expected_version=1)

    def test_invalid_attempt_budget_cannot_be_constructed(self) -> None:
        with self.assertRaises(ValueError):
            job(0)


if __name__ == "__main__":
    unittest.main()
