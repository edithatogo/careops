"""Effective-dated, source-qualified plan-version reference tests."""
from __future__ import annotations
from datetime import date, datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "plan_records.py"
SPEC = spec_from_file_location("mjp_plan_records", SOURCE)
assert SPEC is not None and SPEC.loader is not None
M = module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)
SHA = "f" * 64
ISSUED = datetime(2026, 11, 1, tzinfo=timezone.utc)
AS_OF = datetime(2026, 11, 13, tzinfo=timezone.utc)


def make(**changes):
    data = dict(
        plan_ref="fixture:plan-1", version_ref="fixture:v1",
        submitted_sha256=SHA, policy_snapshot_ref="fixture:policy",
        appointment_ref="fixture:appointment", position_ref="fixture:position",
        service_assignment_ref="fixture:assignment",
        effective_from=date(2026, 11, 1), effective_to=None,
        issued_at=ISSUED, decision_evidence_ref="fixture:decision", state="issued",
    )
    data.update(changes)
    return M.PlanVersion(**data)


def read(versions, day=date(2026, 11, 13), **changes):
    options = dict(plan_ref="fixture:plan-1", date_as_of=day,
                   observed_at=AS_OF, source_read_complete=True)
    options.update(changes)
    return M.read_as_of(versions, **options)


class PlanVersionTests(unittest.TestCase):
    def test_candidate_as_of_never_claims_verified_authority(self):
        result = read([make()])
        self.assertEqual(result["status"], "candidate_issued")
        self.assertEqual(result["version_ref"], "fixture:v1")
        self.assertFalse(result["authority_verified"])

    def test_submitted_version_is_not_issued(self):
        version = make(state="submitted", issued_at=None, decision_evidence_ref=None)
        self.assertEqual(read([version])["status"], "not_issued")

    def test_incomplete_source_is_unknown_not_empty(self):
        result = read([], source_read_complete=False)
        self.assertEqual(result["status"], "unverified_incomplete_source")

    def test_overlapping_versions_rejected(self):
        with self.assertRaises(M.VersionError):
            read([make(), make(version_ref="fixture:v2")])

    def test_future_issuance_not_historically_visible(self):
        future = make(issued_at=datetime(2026, 11, 14, tzinfo=timezone.utc))
        self.assertEqual(read([future])["status"], "not_issued")

    def test_half_open_effective_interval(self):
        self.assertEqual(read([make(effective_to=date(2026, 11, 13))])["status"], "not_issued")

    def test_issued_needs_external_decision_evidence_reference(self):
        with self.assertRaises(M.VersionError):
            make(decision_evidence_ref=None)

    def test_invalid_hash_and_naive_timestamp_rejected(self):
        with self.assertRaises(M.VersionError):
            make(submitted_sha256="bad")
        with self.assertRaises(M.VersionError):
            make(issued_at=datetime(2026, 11, 1))


if __name__ == "__main__":
    unittest.main()
