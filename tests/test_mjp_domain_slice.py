"""Focused source-admission tests: synthetic-only, no tenant or employment records."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "domain.py"
SPEC = spec_from_file_location("careops_mjp_domain_slice", PATH)
assert SPEC is not None and SPEC.loader is not None
DOMAIN = module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = DOMAIN
SPEC.loader.exec_module(DOMAIN)

BASE = {"week": 1, "day": 1, "start_min": 480, "end_min": 540,
        "code": "Clinical", "site": "SYNTHETIC"}


class StrictSessionsTests(unittest.TestCase):
    def test_string_and_numeric_boolean_flags_rejected(self) -> None:
        for field in ("ordinary", "cst"):
            for value in ("false", "true", "0", "1", 0, 1, None):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(DOMAIN.DomainError):
                        DOMAIN.activities_from_sessions([{**BASE, field: value}])

    def test_strict_integer_interval_fields(self) -> None:
        for field in ("week", "day", "start_min", "end_min"):
            for value in (True, False, 1.0, "1"):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(DOMAIN.DomainError):
                        DOMAIN.activities_from_sessions([{**BASE, field: value}])

    def test_codes_and_sites_must_be_nonempty_strings(self) -> None:
        for field in ("code", "site"):
            for value in ("", " ", None, 7):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(DOMAIN.DomainError):
                        DOMAIN.activities_from_sessions([{**BASE, field: value}])

    def test_unknown_field_rejected(self) -> None:
        with self.assertRaises(DOMAIN.DomainError):
            DOMAIN.activities_from_sessions([{**BASE, "role": "self-approved"}])

    def test_overlap_rejected(self) -> None:
        first = DOMAIN.activities_from_sessions([BASE])[0]
        second = DOMAIN.activities_from_sessions([
            {**BASE, "start_min": 520, "end_min": 580}
        ])[0]
        with self.assertRaises(DOMAIN.DomainError):
            DOMAIN.validate_cycle([first, second], 2)

    def test_cst_outside_ordinary_hours_rejected(self) -> None:
        activity = DOMAIN.activities_from_sessions([
            {**BASE, "cst": True, "ordinary": False}
        ])[0]
        with self.assertRaises(DOMAIN.DomainError):
            DOMAIN.validate_cycle([activity], 2)

    def test_balanced_synthetic_plan_not_marked_industrially_compliant(self) -> None:
        sessions = [
            {**BASE, "week": week, "day": day, "end_min": 960,
             "cst": day == 1}
            for week in (1, 2) for day in (1, 2, 3, 4, 5)
        ]
        value = DOMAIN.reconcile_reference_only(sessions, 2, "80", "0.10")
        self.assertEqual(value["planned_ordinary_hours"], "80")
        self.assertEqual(value["planned_cst_hours"], "16")
        self.assertEqual(value["candidate_cst_hours"], "8.00")
        self.assertTrue(value["ordinary_balanced"])
        self.assertEqual(value["policy_status"], "reference_only_unadopted")

    def test_bad_rule_inputs_rejected(self) -> None:
        for bad in ("NaN", "Infinity", True, -1, "1.1", 0.1):
            with self.subTest(value=bad):
                with self.assertRaises(DOMAIN.DomainError):
                    DOMAIN.reconcile_reference_only([], 2, 80, bad)

    def test_valid_strict_flag_roundtrip(self) -> None:
        values = DOMAIN.activities_from_sessions([
            {**BASE, "ordinary": True, "cst": False}
        ])
        DOMAIN.validate_cycle(values, 1)
        self.assertTrue(values[0].ordinary)
        self.assertFalse(values[0].cst)


if __name__ == "__main__":
    unittest.main()
