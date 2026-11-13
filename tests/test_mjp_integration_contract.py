"""Source-only Medical Job Planning contract conformance tests.

No native Power Platform environment, employment policy or identities involved.
Run via CareOps focused unittest after installing the exact pinned CI dependencies.
"""
from __future__ import annotations

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "conductor" / "tracks" / "medical_job_planning_20261113" / "contracts"
SPEC = spec_from_file_location("mjp_semantic_validation", CONTRACTS / "semantic_validation.py")
assert SPEC is not None and SPEC.loader is not None
SEMANTICS = module_from_spec(SPEC)
SPEC.loader.exec_module(SEMANTICS)


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((CONTRACTS / "envelope.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())
        cls.valid = json.loads((CONTRACTS / "fixtures" / "valid-messages.json").read_text(encoding="utf-8"))
        cls.negative = json.loads((CONTRACTS / "fixtures" / "negative-cases.json").read_text(encoding="utf-8"))

    def msg(self, kind: str) -> dict:
        return deepcopy(next(x for x in self.valid if x["message_type"] == kind))

    def assert_valid(self, item: dict) -> None:
        self.assertEqual(list(self.validator.iter_errors(item)), [])
        self.assertEqual(SEMANTICS.semantic_errors(item), [])

    def test_all_eight_positive_fixtures(self) -> None:
        self.assertEqual(len(self.valid), 8)
        self.assertEqual(len(set(m["message_type"] for m in self.valid)), 8)
        for msg in self.valid:
            with self.subTest(message_type=msg["message_type"]):
                self.assert_valid(msg)

    def test_population_mismatch_rejected(self) -> None:
        msg = self.msg("workforce.aggregate")
        msg["payload"]["missing_count"] += 1
        self.assertEqual(list(self.validator.iter_errors(msg)), [])
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_false_complete_coverage_rejected(self) -> None:
        msg = self.msg("workforce.aggregate")
        msg["quality"]["status"] = "complete"
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_scope_mismatch_rejected(self) -> None:
        msg = self.msg("workforce.aggregate")
        msg["context"]["scope_key"] = "fixture/other-service"
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_wrong_purpose_rejected(self) -> None:
        msg = self.msg("workforce.aggregate")
        msg["purpose"] = "workflow-decision"
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_inverted_effective_time_rejected(self) -> None:
        msg = self.msg("policy.reference")
        msg["effective_from"] = "2026-12-01T00:00:00Z"
        msg["effective_to"] = "2026-11-01T00:00:00Z"
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_condition_requires_evidence(self) -> None:
        msg = self.msg("approval.result")
        msg["payload"]["outcome"] = "conditional_approval"
        self.assertGreater(len(list(self.validator.iter_errors(msg))), 0)

    def test_suppression_reconciles_envelope(self) -> None:
        msg = self.msg("workforce.aggregate")
        msg["quality"]["suppression"] = "applied"
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_source_reference_unverified_cannot_claim_complete(self) -> None:
        msg = self.msg("source.reference")
        msg["quality"]["status"] = "complete"
        self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_invalid_session_bool_string_rejected(self) -> None:
        schema = json.loads((CONTRACTS / "session.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        session = {"week": 1, "day": 1, "start_min": 480,
                   "end_min": 600, "code": "synthetic-care", "site": "fictional", "ordinary": True, "cst": False}
        self.assertFalse(list(validator.iter_errors(session)))
        session["ordinary"] = "false"
        self.assertTrue(list(validator.iter_errors(session)))
        session["ordinary"] = False
        session["cst"] = "false"
        self.assertTrue(list(validator.iter_errors(session)))

    def test_negative_schema_cases_are_rejected(self) -> None:
        for case in self.negative["cases"]:
            if case["expect"] != "schema_reject":
                continue
            with self.subTest(case=case["id"]):
                msg = self.msg(case["type"])
                change = case["change"]
                if "remove" in change:
                    keys = change["remove"].split(".")
                    cursor = msg
                    for k in keys[:-1]:
                        cursor = cursor[k]
                    cursor.pop(keys[-1])
                else:
                    keys = change["path"].split(".")
                    cursor = msg
                    for k in keys[:-1]:
                        cursor = cursor[k]
                    cursor[keys[-1]] = change["value"]
                errors = list(self.validator.iter_errors(msg))
                self.assertTrue(errors, f"Case {case['id']} unexpectedly accepted by schema")


    def test_negative_semantic_cases_are_rejected(self) -> None:
        for case in self.negative["cases"]:
            if case["expect"] != "semantic_reject":
                continue
            with self.subTest(case=case["id"]):
                msg = self.msg(case["type"])
                keys = case["change"]["path"].split(".")
                cursor = msg
                for key in keys[:-1]:
                    cursor = cursor[key]
                cursor[keys[-1]] = case["change"]["value"]
                self.assertFalse(list(self.validator.iter_errors(msg)))
                self.assertTrue(SEMANTICS.semantic_errors(msg))

    def test_metric_dictionary_references_are_explicit(self) -> None:
        dictionary = json.loads((CONTRACTS / "metric-dictionary.json").read_text(encoding="utf-8"))
        definitions = {row["metric_id"]: row for row in dictionary["metrics"]}
        for kind in ("workforce.aggregate", "costing.aggregate"):
            msg = self.msg(kind)
            definition = definitions[msg["payload"]["metric_id"]]
            self.assertEqual(msg["payload"]["metric_definition_ref"], definition["definition_ref"])
            self.assertEqual(msg["payload"]["metric_version"], definition["metric_version"])


    def test_activity_taxonomy_preserves_independent_axes(self) -> None:
        taxonomy = json.loads((CONTRACTS / "activity-taxonomy.json").read_text(encoding="utf-8"))
        axes = taxonomy["axes"]
        self.assertIn("ordinary", axes["time_class"])
        self.assertIn("recall", axes["time_class"])
        self.assertIn("disputed", axes["cst_treatment"])
        self.assertIn("observed", axes["evidence_state"])
        for example in taxonomy["syntheticExamples"]:
            self.assertTrue(set(example["domains"]).issubset(set(axes["activity_domain"])))
            self.assertIn(example["candidate_cst_treatment"], axes["cst_treatment"])
            self.assertIn(example["suggested_service_coverage"], axes["service_coverage"])
            self.assertNotEqual(example["candidate_cst_treatment"], "adopted_eligible")

    def test_native_only_cases_are_not_misreported(self) -> None:
        self.assertTrue(any(c["expect"].startswith("runtime_") for c in self.negative["cases"]))
        self.assertIn("contract-test-design-only", self.negative["status"])


if __name__ == "__main__":
    unittest.main()
