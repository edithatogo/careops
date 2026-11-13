"""Synthetic review-queue transition contracts; no native decisions or side effects."""
from __future__ import annotations

import unittest

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from registration_assurance.review import (  # noqa: E402
    ReviewConflict,
    propose_review,
    apply_review,
)


def observation(status: str = "suspended", *, conditions: tuple[str, ...] = (),
                observation_id: str = "o1", watch: str = "watch:a") -> dict[str, object]:
    return {
        "watchRef": watch,
        "observationId": observation_id,
        "practitioner": {"regulator": "AHPRA", "registrationNumber": "TEST-001"},
        "provider": {"kind": "AHPRA_PIE_FIND", "qualificationRef": "fictional"},
        "sourceHealth": "healthy",
        "signal": {"registrationStatus": status, "identityState": "matched",
                   "expiryDate": None, "conditionsIndicator": "present" if conditions else "absent"},
        "registrationDetail": {
            "nativeStatusCode": "synthetic-status", "categories": ["specialist"],
            "specialties": ["synthetic-specialty"], "endorsements": [],
            "restrictions": [{"kind": "condition", "nativeCode": name} for name in conditions],
        },
        "evidence": {"sourceRef": "test:evidence", "asOfUtc": "2026-11-13T00:00:00Z"},
    }


class ReviewQueueTests(unittest.TestCase):
    def test_adverse_observation_creates_one_pending_exception(self) -> None:
        proposed = propose_review(None, observation(), {"disposition": "potential_adverse_change",
            "human_review_required": True, "reason_codes": ["verified_adverse"]})
        self.assertIsNotNone(proposed)
        self.assertEqual(proposed["reviewState"], "pending")
        self.assertEqual(proposed["reviewVersion"], 1)
        self.assertFalse(proposed["practiceAuthorised"])
        self.assertEqual(proposed["watchRef"], "watch:a")

    def test_no_exception_for_non_review_source(self) -> None:
        self.assertIsNone(propose_review(None, observation(status="registered"),
            {"disposition": "source_verified", "human_review_required": False, "reason_codes": []}))

    def test_idempotent_facts_ignore_new_receipt_and_timestamp(self) -> None:
        item = observation()
        result = {"disposition": "potential_adverse_change", "human_review_required": True,
                  "reason_codes": ["verified_adverse"]}
        first = propose_review(None, item, result)
        resolved = apply_review(first, "held", actor_ref="test:reviewer",
                                evidence_ref="test:manual", expected_version=1,
                                reviewed_at_utc="2026-11-13T02:00:00Z")
        second = observation(observation_id="o2")
        second["evidence"]["sourceRef"] = "test:new-check"
        second["evidence"]["asOfUtc"] = "2026-11-14T00:00:00Z"
        self.assertEqual(propose_review(resolved, second, result), resolved)

    def test_material_restriction_change_reopens_and_preserves_history(self) -> None:
        result = {"disposition": "restriction_review", "human_review_required": True,
                  "reason_codes": ["conditions_or_undertakings_require_review"]}
        first = propose_review(None, observation(status="registered", conditions=("A",)), result)
        reviewed = apply_review(first, "verified", actor_ref="test:reviewer",
                                evidence_ref="test:receipt", expected_version=1,
                                reviewed_at_utc="2026-11-13T02:00:00Z")
        changed = propose_review(reviewed, observation(status="registered", conditions=("B",),
                                                       observation_id="o2"), result)
        self.assertEqual(changed["reviewState"], "pending")
        self.assertEqual(changed["reviewVersion"], 3)
        self.assertEqual(len(changed["reviewHistory"]), 1)
        self.assertEqual(changed["reviewHistory"][0]["disposition"], "verified")

    def test_stale_review_action_is_rejected(self) -> None:
        first = propose_review(None, observation(), {
            "disposition": "potential_adverse_change", "human_review_required": True,
            "reason_codes": ["verified_adverse"]})
        with self.assertRaises(ReviewConflict):
            apply_review(first, "verified", actor_ref="test:r", evidence_ref="test:manual",
                         expected_version=0, reviewed_at_utc="2026-11-13T02:00:00Z")

    def test_review_requires_actor_time_evidence_and_allowed_disposition(self) -> None:
        first = propose_review(None, observation(), {
            "disposition": "potential_adverse_change", "human_review_required": True,
            "reason_codes": ["verified_adverse"]})
        for disposition, actor, evidence, at in [
            ("unknown", "test:r", "test:e", "2026-11-13T02:00:00Z"),
            ("verified", "", "test:e", "2026-11-13T02:00:00Z"),
            ("verified", "test:r", "", "2026-11-13T02:00:00Z"),
            ("verified", "test:r", "test:e", "invalid"),
        ]:
            with self.subTest(disposition=disposition, actor=actor, evidence=evidence, at=at):
                with self.assertRaises(ValueError):
                    apply_review(first, disposition, actor_ref=actor, evidence_ref=evidence,
                                 expected_version=1, reviewed_at_utc=at)

    def test_identity_mismatch_does_not_reuse_review_case(self) -> None:
        result = {"disposition": "restriction_review", "human_review_required": True, "reason_codes": []}
        first = propose_review(None, observation(status="registered", conditions=("A",)), result)
        changed = observation(status="registered", conditions=("A",), observation_id="o2")
        changed["practitioner"]["registrationNumber"] = "TEST-002"
        with self.assertRaises(ReviewConflict):
            propose_review(first, changed, result)

    def test_watch_id_change_cannot_reuse_case(self) -> None:
        result = {"disposition": "potential_adverse_change", "human_review_required": True, "reason_codes": []}
        first = propose_review(None, observation(), result)
        with self.assertRaises(ReviewConflict):
            propose_review(first, observation(watch="watch:b"), result)

    def test_actor_disposition_does_not_grant_practice_authority(self) -> None:
        result = {"disposition": "potential_adverse_change", "human_review_required": True, "reason_codes": []}
        first = propose_review(None, observation(), result)
        reviewed = apply_review(first, "verified", actor_ref="test:reviewer",
                                evidence_ref="test:receipt", expected_version=1,
                                reviewed_at_utc="2026-11-13T02:00:00Z")
        self.assertFalse(reviewed["practiceAuthorised"])
        self.assertNotIn("credentialingStatus", reviewed)

    def test_cannot_review_an_already_reviewed_revision(self) -> None:
        result = {"disposition": "potential_adverse_change", "human_review_required": True, "reason_codes": []}
        first = propose_review(None, observation(), result)
        reviewed = apply_review(first, "verified", actor_ref="test:r", evidence_ref="test:manual",
                                expected_version=1, reviewed_at_utc="2026-11-13T02:00:00Z")
        with self.assertRaises(ReviewConflict):
            apply_review(reviewed, "verified", actor_ref="test:r", evidence_ref="test:manual",
                         expected_version=2, reviewed_at_utc="2026-11-13T03:00:00Z")


if __name__ == "__main__":
    unittest.main()
