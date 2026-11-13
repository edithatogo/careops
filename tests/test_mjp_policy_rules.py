"""Synthetic rule-reference and safety tests: no live policy authority."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

FILE = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "policy_rules.py"
SPEC = spec_from_file_location("mjp_policy_rules", FILE)
assert SPEC is not None and SPEC.loader is not None
RULES = module_from_spec(SPEC)
sys.modules[SPEC.name] = RULES
SPEC.loader.exec_module(RULES)


def pack(**changes):
    inputs = dict(
        rule_key="fixture:smocst", edition="fixture-1", source_ref="fixture:policy",
        source_sha256="a" * 64, clause_ref="fixture:clause",
        effective_from=date(2026, 1, 1), effective_to=None,
        status="reference_only", adoption_ref=None,
        eligible_classifications=frozenset({"fictional-smotype"}),
        fraction=Decimal("0.10"),
    )
    inputs.update(changes)
    return RULES.RulePack(**inputs)


class RuleTests(unittest.TestCase):
    def test_unadopted_cannot_certify_compliance(self):
        x = RULES.assess_cst(
            pack(), classification="fictional-smotype", as_of=date(2026, 11, 13),
            contracted_hours="80", planned_hours="6", observed_hours="3",
            verified_contract=True,
        )
        self.assertEqual(x["candidate_minimum_hours"], "8.00")
        self.assertEqual(x["planned_shortfall_hours"], "2.00")
        self.assertEqual(x["actual_access_shortfall_hours"], "5.00")
        self.assertEqual(x["authority_status"], "reference_only")
        self.assertFalse(x["approval_allowed"])

    def test_adopted_still_requires_human_approval(self):
        x = RULES.assess_cst(
            pack(status="adopted", adoption_ref="fixture:review"),
            classification="fictional-smotype", as_of=date(2026, 11, 13),
            contracted_hours="80", planned_hours="8",
            observed_hours=None, verified_contract=True,
        )
        self.assertTrue(x["rules_operative"])
        self.assertFalse(x["approval_allowed"])
        self.assertEqual(x["observed_data_status"], "not_observed")

    def test_ineligible_classification_never_inherits_fraction(self):
        x = RULES.assess_cst(
            pack(), classification="fictional-other", as_of=date(2026, 11, 13),
            contracted_hours="80", planned_hours="8",
            observed_hours=None, verified_contract=True,
        )
        self.assertEqual(x["eligibility"], "not_established")
        self.assertIsNone(x["candidate_minimum_hours"])

    def test_effective_dates(self):
        for as_of in (date(2025, 12, 31), date(2027, 1, 1)):
            with self.subTest(as_of=as_of):
                x = RULES.assess_cst(
                    pack(effective_to=date(2026, 12, 31)),
                    classification="fictional-smotype", as_of=as_of,
                    contracted_hours="80", planned_hours="8",
                    observed_hours=None, verified_contract=True,
                )
                self.assertEqual(x["eligibility"], "not_established")

    def test_adoption_source_and_fraction_validation(self):
        for changes in (
            {"status": "adopted", "adoption_ref": None},
            {"source_sha256": "not_a_sha"},
            {"fraction": Decimal("1.4")},
            {"status": "implicitly_approved"},
        ):
            with self.subTest(changes=changes), self.assertRaises(RULES.RuleError):
                pack(**changes)

    def test_no_implicit_numeric_or_boolean_conversion(self):
        for value in (False, True, 0.1, "NaN", "Infinity", "-3", ""):
            with self.subTest(value=value), self.assertRaises(RULES.RuleError):
                RULES.assess_cst(
                    pack(), classification="fictional-smotype",
                    as_of=date(2026, 11, 13), contracted_hours=value,
                    planned_hours="8", observed_hours=None, verified_contract=True,
                )

    def test_unverified_source_blocks_operative_rule(self):
        x = RULES.assess_cst(
            pack(status="adopted", adoption_ref="fixture:review"),
            classification="fictional-smotype", as_of=date(2026, 11, 13),
            contracted_hours="80", planned_hours="8",
            observed_hours=None, verified_contract=False,
        )
        self.assertFalse(x["rules_operative"])
        self.assertEqual(x["eligibility"], "source_unverified")

    def test_planned_vs_observed_separate(self):
        x = RULES.assess_cst(
            pack(), classification="fictional-smotype", as_of=date(2026, 11, 13),
            contracted_hours="80", planned_hours="8",
            observed_hours="2", verified_contract=True,
        )
        self.assertEqual(x["planned_shortfall_hours"], "0.00")
        self.assertEqual(x["actual_access_shortfall_hours"], "6.00")


if __name__ == "__main__":
    unittest.main()
