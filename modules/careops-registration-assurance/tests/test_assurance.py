"""Offline, fictional-only registration assurance regression tests."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from registration_assurance.assurance import (  # noqa: E402
    assess_engagement_coverage, assess_observation, reconcile_observations,
)


def observation(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "observationId": "test:obs-1",
        "watchRef": "test:watch-1",
        "practitioner": {"regulator": "AHPRA", "registrationNumber": "TEST-0001"},
        "provider": {"kind": "AHPRA_PIE_FIND", "evidenceCeiling": "qualified_regulatory",
                     "qualificationRef": "test:contract-1", "mappingVersion": "1.0"},
        "sourceHealth": "healthy",
        "observedAtUtc": "2026-11-13T00:00:00Z",
        "evidence": {"sourceRef": "test:receipt-1", "asOfUtc": "2026-11-12T23:30:00Z"},
        "signal": {"identityState": "matched", "registrationStatus": "registered",
                   "expiryDate": "2026-12-01", "conditionsIndicator": "absent"},
        "registrationDetail": {"categories": ["general"], "nativeStatusCode": "synthetic:general",
                               "sourceVocabularyVersion": "test:v1", "restrictions": []},
    }
    base.update(overrides)
    return base


class RegistrationAssuranceTests(unittest.TestCase):
    def test_source_verified_does_not_grant_practice_authority(self) -> None:
        r = assess_observation(observation(), now="2026-11-13T00:00:00Z")
        self.assertEqual(r["disposition"], "source_verified")
        self.assertFalse(r["practice_authorised"])

    def test_mock_registration_cannot_pass_as_real(self) -> None:
        item = observation(provider={"kind": "MOCK", "evidenceCeiling": "test_only",
                                     "qualificationRef": None, "mappingVersion": "test"})
        self.assertEqual(assess_observation(item)["disposition"], "synthetic_only")

    def test_autocomplete_registered_is_not_regulator_verification(self) -> None:
        item = observation(provider={"kind": "AHPRA_PUBLIC_AUTOCOMPLETE", "evidenceCeiling": "discovery_only",
                                     "qualificationRef": None, "mappingVersion": "test"})
        self.assertEqual(assess_observation(item)["disposition"], "discovery_only")

    def test_pie_identity_cannot_make_registration_status_claim(self) -> None:
        item = observation(provider={"kind": "AHPRA_PIE_IDENTITY", "evidenceCeiling": "qualified_identity_only",
                                     "qualificationRef": "test:identity", "mappingVersion": "test"})
        self.assertEqual(assess_observation(item)["disposition"], "identity_evidence_only")

    def test_qualified_provider_with_missing_agreement_is_held(self) -> None:
        item = observation(provider={"kind": "AHPRA_PIE_FIND", "evidenceCeiling": "qualified_regulatory",
                                     "qualificationRef": None, "mappingVersion": "1"})
        self.assertEqual(assess_observation(item)["disposition"], "unqualified_source")

    def test_provider_ceiling_substitution_is_held(self) -> None:
        item = observation(provider={"kind": "AHPRA_PIE_FIND", "evidenceCeiling": "human_verified",
                                     "qualificationRef": "test:fake", "mappingVersion": "1"})
        self.assertEqual(assess_observation(item)["disposition"], "unqualified_source")

    def test_name_only_identity_is_unresolved(self) -> None:
        item = observation(practitioner={"regulator": "AHPRA", "registrationNumber": None})
        self.assertEqual(assess_observation(item)["disposition"], "identity_unresolved")

    def test_blocked_source_never_reports_adverse_change(self) -> None:
        item = observation(sourceHealth="blocked", signal={"identityState": "matched",
            "registrationStatus": "suspended", "expiryDate": None, "conditionsIndicator": "unknown"})
        r = assess_observation(item)
        self.assertEqual(r["disposition"], "source_unavailable")
        self.assertNotIn("verified_adverse", r["reason_codes"])

    def test_old_evidence_is_explicitly_stale(self) -> None:
        item = observation(evidence={"sourceRef": "test:receipt", "asOfUtc": "2026-10-01T00:00:00Z"})
        self.assertEqual(assess_observation(item, now="2026-11-13T00:00:00Z")["disposition"], "stale_source")

    def test_future_source_as_of_is_rejected(self) -> None:
        item = observation(evidence={"sourceRef": "test:receipt", "asOfUtc": "2026-11-15T00:00:00Z"})
        self.assertEqual(assess_observation(item, now="2026-11-13T00:00:00Z")["disposition"], "temporal_conflict")

    def test_adverse_regulatory_signal_is_human_review_only(self) -> None:
        item = observation(signal={"identityState": "matched", "registrationStatus": "suspended",
                                   "expiryDate": "2026-12-01", "conditionsIndicator": "unknown"})
        r = assess_observation(item)
        self.assertEqual(r["disposition"], "potential_adverse_change")
        self.assertTrue(r["human_review_required"])
        self.assertFalse(r["practice_authorised"])

    def test_non_practising_category_is_not_approved_practice(self) -> None:
        item = observation(registrationDetail={"categories": ["non_practising"],
            "nativeStatusCode": "test:np", "sourceVocabularyVersion": "test:v1", "restrictions": []})
        self.assertEqual(assess_observation(item)["disposition"], "practice_category_review")

    def test_limited_provisional_unknown_and_other_categories_need_review(self) -> None:
        for category in ("limited", "provisional", "unknown", "other"):
            with self.subTest(category=category):
                item = observation(registrationDetail={
                    "categories": [category], "nativeStatusCode": "test:" + category,
                    "sourceVocabularyVersion": "test:v1", "restrictions": [],
                })
                self.assertEqual(assess_observation(item)["disposition"], "practice_category_review")

    def test_restriction_is_not_reduced_to_boolean(self) -> None:
        item = observation(registrationDetail={"categories": ["specialist"], "nativeStatusCode": "test:s",
            "sourceVocabularyVersion": "test:v1", "restrictions": [{"type": "supervision", "evidenceRef": "test:evidence"}]})
        self.assertEqual(assess_observation(item)["disposition"], "restriction_review")

    def test_expiry_date_is_not_deregistration(self) -> None:
        item = observation(signal={"identityState": "matched", "registrationStatus": "registered",
            "expiryDate": "2026-11-01", "conditionsIndicator": "absent"})
        r = assess_observation(item)
        self.assertEqual(r["disposition"], "expiry_review")
        self.assertNotIn("verified_adverse", r["reason_codes"])

    def test_repeat_and_out_of_order_reconciliation(self) -> None:
        old = observation()
        duplicate = observation(observationId="test:retry")
        newer = observation(observationId="test:new",
            evidence={"sourceRef": "test:new", "asOfUtc": "2026-11-13T00:00:00Z"})
        r = reconcile_observations([old, duplicate, newer, old])
        self.assertEqual(len(r["accepted"]), 2)
        self.assertEqual(len(r["duplicates"]), 2)
        self.assertEqual(r["currentObservationId"], "test:new")

    def test_same_time_conflicting_status_cannot_win(self) -> None:
        one = observation()
        two = observation(observationId="test:other",
            signal={**one["signal"], "registrationStatus": "suspended"})
        r = reconcile_observations([one, two])
        self.assertEqual(r["conflicts"], ["test:other"])
        self.assertEqual(r["currentObservationId"], "test:obs-1")

    def test_delayed_old_observation_does_not_replace_current(self) -> None:
        newer = observation(observationId="test:new",
            evidence={"sourceRef": "test:new", "asOfUtc": "2026-11-13T00:00:00Z"})
        old = observation(observationId="test:old",
            evidence={"sourceRef": "test:old", "asOfUtc": "2026-11-12T00:00:00Z"})
        r = reconcile_observations([newer, old])
        self.assertEqual(r["currentObservationId"], "test:new")
        self.assertEqual(r["superseded"], ["test:old"])

    def test_active_engagements_are_denominator_including_rural_locum(self) -> None:
        engagements = [
            {"engagementRef": "test:e1", "watchRef": "test:w1", "facilityRef": "test:cairns",
             "kind": "vmo", "active": True},
            {"engagementRef": "test:e2", "watchRef": "test:w2", "facilityRef": "test:rural",
             "kind": "locum", "active": True},
            {"engagementRef": "test:e3", "watchRef": "test:w3", "facilityRef": "test:rural",
             "kind": "contractor", "active": False},
        ]
        watches = [{"watchRef": "test:w1", "registrationNumber": "TEST-0001", "enabled": True}]
        r = assess_engagement_coverage(engagements, watches)
        self.assertEqual((r["eligible"], r["covered"]), (2, 1))
        self.assertEqual(r["unmatched"], ["test:e2"])
        self.assertEqual(r["byFacility"]["test:rural"]["eligible"], 1)

    def test_disabled_watch_does_not_count_as_coverage(self) -> None:
        en = [{"engagementRef": "test:e1", "watchRef": "test:w1", "facilityRef": "test:site",
               "kind": "locum", "active": True}]
        w = [{"watchRef": "test:w1", "registrationNumber": "TEST-0001", "enabled": False}]
        self.assertEqual(assess_engagement_coverage(en, w)["covered"], 0)

    def test_ambiguous_duplicate_watch_cannot_count_as_coverage(self) -> None:
        en = [{"engagementRef": "test:e1", "watchRef": "test:w1", "facilityRef": "test:site",
               "kind": "locum", "active": True}]
        w = [{"watchRef": "test:w1", "registrationNumber": "TEST-0001", "enabled": True},
             {"watchRef": "test:w1", "registrationNumber": "TEST-0002", "enabled": True}]
        r = assess_engagement_coverage(en, w)
        self.assertEqual(r["covered"], 0)
        self.assertEqual(r["ambiguous"], ["test:e1"])


if __name__ == "__main__":
    unittest.main()
