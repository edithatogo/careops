"""Source capability gate tests; all values are fabricated."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from registration_assurance.qualification import Qualification, assess_qualified  # noqa: E402


def observation() -> dict[str, object]:
    return {
        "schemaVersion": "1.1.0",
        "observationId": "test:obs",
        "watchRef": "test:watch",
        "practitioner": {"regulator": "AHPRA", "registrationNumber": "TEST-001"},
        "provider": {"kind": "AHPRA_PIE_FIND", "qualificationRef": "test:q1",
                     "evidenceCeiling": "qualified_regulatory", "mappingVersion": "test:m1"},
        "sourceHealth": "healthy",
        "observedAtUtc": "2026-11-13T09:00:00Z",
        "evidence": {"sourceRef": "test:source", "asOfUtc": "2026-11-13T08:00:00Z"},
        "signal": {"identityState": "matched", "registrationStatus": "registered",
                   "expiryDate": "2026-12-01", "conditionsIndicator": "absent"},
        "registrationDetail": {"nativeStatusCode": "test:general", "sourceVocabularyVersion": "test:reg-1",
                               "categories": ["general"], "specialties": [], "endorsements": [], "restrictions": []},
    }


def policy(**changes: object) -> Qualification:
    args = dict(provider_kind="AHPRA_PIE_FIND", qualification_ref="test:q1",
                purposes=frozenset({"credentialing_read"}), approved_vocabulary=frozenset({"test:reg-1"}),
                enabled=True, effective_from_utc="2026-11-01T00:00:00Z",
                effective_to_utc="2026-12-01T00:00:00Z", max_source_age_minutes=120)
    args.update(changes)
    return Qualification(**args)


class QualificationTests(unittest.TestCase):
    NOW = "2026-11-13T09:00:00Z"

    def assess(self, value: dict[str, object] | None = None,
               gate: Qualification | None = None, purpose: str = "credentialing_read") -> dict[str, object]:
        return assess_qualified(value if value is not None else observation(),
                                qualification=gate, purpose=purpose, now_utc=self.NOW)

    def test_without_trusted_qualification_is_held(self) -> None:
        self.assertEqual(self.assess()["disposition"], "unqualified_source")

    def test_qualified_fixture_observation_is_not_practice_authorisation(self) -> None:
        result = self.assess(gate=policy())
        self.assertEqual(result["disposition"], "source_verified")
        self.assertFalse(result["practice_authorised"])

    def test_disabled_provider_is_held(self) -> None:
        self.assertEqual(self.assess(gate=policy(enabled=False))["disposition"], "unqualified_source")

    def test_wrong_source_id_kind_or_purpose_is_held(self) -> None:
        for change, purpose in [
            ({"qualification_ref": "test:other"}, "credentialing_read"),
            ({"provider_kind": "AHPRA_PIE_IDENTITY"}, "credentialing_read"),
            ({}, "workforce_write"),
        ]:
            with self.subTest(change=change, purpose=purpose):
                self.assertEqual(self.assess(gate=policy(**change), purpose=purpose)["disposition"],
                                 "unqualified_source")

    def test_expired_or_not_yet_effective_provider_is_held(self) -> None:
        for period in [
            {"effective_from_utc": "2026-11-14T00:00:00Z", "effective_to_utc": "2026-12-01T00:00:00Z"},
            {"effective_to_utc": "2026-11-12T00:00:00Z"},
        ]:
            with self.subTest(period=period):
                self.assertEqual(self.assess(gate=policy(**period))["disposition"], "unqualified_source")

    def test_lagging_source_cannot_be_laundered_by_recent_poll(self) -> None:
        value = observation()
        value["observedAtUtc"] = self.NOW
        value["evidence"]["asOfUtc"] = "2026-11-13T06:00:00Z"
        self.assertEqual(self.assess(value, gate=policy())["disposition"], "stale_source")

    def test_source_vocabulary_mismatch_is_held(self) -> None:
        value = observation()
        value["registrationDetail"]["sourceVocabularyVersion"] = "test:reg-new"
        self.assertEqual(self.assess(value, gate=policy())["disposition"], "unqualified_source")

    def test_legacy_version_cannot_prove_current_registration(self) -> None:
        value = observation()
        value["schemaVersion"] = "1.0.0"
        value.pop("registrationDetail")
        self.assertEqual(self.assess(value, gate=policy())["disposition"], "verification_required")

    def test_unknown_future_envelope_is_held(self) -> None:
        value = observation()
        value["schemaVersion"] = "1.2.0"
        self.assertEqual(self.assess(value, gate=policy())["disposition"], "unqualified_source")

    def test_adverse_fact_is_only_referred_for_human_review(self) -> None:
        value = observation()
        value["signal"]["registrationStatus"] = "suspended"
        result = self.assess(value, gate=policy())
        self.assertEqual(result["disposition"], "potential_adverse_change")
        self.assertTrue(result["human_review_required"])
        self.assertFalse(result["practice_authorised"])

    def test_blocked_provider_cannot_disclose_adverse_or_clean_status(self) -> None:
        value = observation()
        value["sourceHealth"] = "blocked"
        self.assertEqual(self.assess(value, gate=policy())["disposition"], "source_unavailable")

    def test_invalid_policy_inputs_fail_at_construct(self) -> None:
        for change in [{"max_source_age_minutes": 0}, {"effective_to_utc": "2026-10-01T00:00:00Z"},
                       {"purposes": frozenset()}, {"qualification_ref": ""}]:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    policy(**change)


if __name__ == "__main__":
    unittest.main()
