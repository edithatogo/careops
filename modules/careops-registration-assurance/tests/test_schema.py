"""JSON Schema 2020-12 contract tests; uses CareOps's hashed CI jsonschema pin."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


SCHEMA = (Path(__file__).resolve().parents[3] /
          "conductor/tracks/registration_assurance_20261113/registration-observation.schema.json")


def source_sample(version: str = "1.1.0") -> dict[str, object]:
    result: dict[str, object] = {
        "schemaVersion": version, "observationId": "test:o1", "watchRef": "test:w1",
        "practitioner": {"regulator": "AHPRA", "registrationNumber": "TEST-0001"},
        "provider": {"kind": "AHPRA_PIE_FIND", "qualificationRef": "test:qualified",
                     "evidenceCeiling": "qualified_regulatory", "mappingVersion": "test:v1"},
        "sourceHealth": "healthy", "observedAtUtc": "2026-11-13T00:00:00Z",
        "evidence": {"sourceRef": "test:source", "asOfUtc": "2026-11-12T23:00:00Z",
                     "payloadSha256": "a" * 64, "sourceRevision": "test:v1",
                     "classification": "synthetic"},
        "signal": {"identityState": "matched", "registrationStatus": "registered",
                   "expiryDate": "2026-12-01", "conditionsIndicator": "absent"},
        "assessment": {"outcome": "no_material_change", "reviewState": "pending",
                       "ruleVersion": "test:v1", "reasonCodes": []},
        "correlationId": "test:correlation", "idempotencyKey": "test:replay",
    }
    if version == "1.1.0":
        result["registrationDetail"] = {
            "nativeStatusCode": "test:general", "sourceVocabularyVersion": "test:registry-v1",
            "categories": ["general"], "specialties": [], "endorsements": [],
            "restrictions": [],
        }
    return result


class ObservationSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def assert_invalid(self, value: dict[str, object]) -> None:
        with self.assertRaises(ValidationError):
            self.validator.validate(value)

    def test_qualified_legacy_and_detail_envelopes_validate(self) -> None:
        for version in ("1.0.0", "1.1.0"):
            with self.subTest(version=version):
                self.validator.validate(source_sample(version))

    def test_future_minor_and_major_are_not_automatically_accepted(self) -> None:
        for version in ("1.2.0", "2.0.0", "invalid"):
            with self.subTest(version=version):
                self.assert_invalid(source_sample(version))

    def test_11_requires_lossless_registration_detail(self) -> None:
        value = source_sample()
        del value["registrationDetail"]
        self.assert_invalid(value)

    def test_11_details_require_native_status_on_regulator_fact(self) -> None:
        value = source_sample()
        value["registrationDetail"]["nativeStatusCode"] = None
        self.assert_invalid(value)

    def test_discovery_suggestion_cannot_claim_registered(self) -> None:
        value = source_sample()
        value["provider"] = {"kind": "AHPRA_PUBLIC_AUTOCOMPLETE", "qualificationRef": None,
                             "evidenceCeiling": "discovery_only", "mappingVersion": "test"}
        self.assert_invalid(value)

    def test_pie_identity_only_cannot_make_registration_status_claim(self) -> None:
        value = source_sample()
        value["provider"] = {"kind": "AHPRA_PIE_IDENTITY", "qualificationRef": "test:q",
                             "evidenceCeiling": "qualified_identity_only", "mappingVersion": "test"}
        self.assert_invalid(value)

    def test_find_source_cannot_forge_human_verification_ceiling(self) -> None:
        value = source_sample()
        value["provider"]["evidenceCeiling"] = "human_verified"
        self.assert_invalid(value)

    def test_qualified_regulatory_claim_must_have_identity_and_evidence(self) -> None:
        for field, bad in (("qualificationRef", None), ("kind", "MOCK")):
            value = source_sample()
            value["provider"][field] = bad
            self.assert_invalid(value)
        value = source_sample()
        value["signal"]["identityState"] = "candidate"
        self.assert_invalid(value)

    def test_provider_fault_cannot_contain_qualified_status_claim(self) -> None:
        for fault in ("blocked", "rate_limited", "schema_drift", "stale"):
            with self.subTest(fault=fault):
                value = source_sample()
                value["sourceHealth"] = fault
                self.assert_invalid(value)

    def test_restricted_evidence_requires_structured_ref(self) -> None:
        value = source_sample()
        value["registrationDetail"]["restrictions"] = [
            {"kind": "supervision", "evidenceRef": "test:restricted", "nativeCode": "test:s1"}
        ]
        self.validator.validate(value)
        value["registrationDetail"]["restrictions"][0]["evidenceRef"] = ""
        self.assert_invalid(value)

    def test_invalid_date_and_time_are_not_accepted(self) -> None:
        value = source_sample()
        value["signal"]["expiryDate"] = "2026-13-99"
        self.assert_invalid(value)
        value = source_sample()
        value["observedAtUtc"] = "not-a-date"
        self.assert_invalid(value)


if __name__ == "__main__":
    unittest.main()
