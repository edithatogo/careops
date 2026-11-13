"""Metamorphic/property tests for safety invariants (fabricated observations only)."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from registration_assurance.assurance import assess_observation, assess_engagement_coverage  # noqa: E402
from registration_assurance.qualification import assess_qualified  # noqa: E402
from registration_assurance.review import propose_review, apply_review  # noqa: E402

from test_qualification import observation as qualified_observation, policy  # noqa: E402
from test_review import observation as review_observation  # noqa: E402


class SafetyProperties(unittest.TestCase):
    @settings(max_examples=40, deadline=None)
    @given(st.sampled_from(["blocked", "rate_limited", "transport_error", "schema_drift", "stale", "unknown"]),
           st.sampled_from(["registered", "not_registered", "cancelled", "suspended"]))
    def test_unavailable_source_never_produces_regulator_status(self, health: str, status: str) -> None:
        item = qualified_observation()
        item["sourceHealth"] = health
        item["signal"]["registrationStatus"] = status
        result = assess_observation(item)
        self.assertEqual(result["disposition"], "source_unavailable")
        self.assertFalse(result["practice_authorised"])
        self.assertNotIn("verified_adverse", result["reason_codes"])

    @settings(max_examples=40, deadline=None)
    @given(st.text(min_size=0, max_size=64))
    def test_undocumented_suggestion_never_proves_status(self, sample: str) -> None:
        item = qualified_observation()
        item["practitioner"]["registrationNumber"] = sample
        item["provider"] = {"kind": "AHPRA_PUBLIC_AUTOCOMPLETE",
                            "qualificationRef": None, "evidenceCeiling": "discovery_only"}
        self.assertEqual(assess_observation(item)["disposition"], "discovery_only")

    @settings(max_examples=40, deadline=None)
    @given(st.integers(min_value=121, max_value=10000))
    def test_qualified_provider_rejects_older_than_approved_source(self, age_minutes: int) -> None:
        from datetime import datetime, timedelta, timezone
        now = datetime(2026, 11, 13, 9, tzinfo=timezone.utc)
        as_of = now - timedelta(minutes=age_minutes)
        item = qualified_observation()
        item["evidence"]["asOfUtc"] = as_of.isoformat()
        result = assess_qualified(item, qualification=policy(), purpose="credentialing_read",
                                  now_utc=now.isoformat())
        self.assertEqual(result["disposition"], "stale_source")

    @settings(max_examples=40, deadline=None)
    @given(st.permutations(["condition-A", "condition-B", "condition-C"]))
    def test_reordering_restrictions_does_not_reopen_review(self, names: list[str]) -> None:
        assess = {"disposition": "restriction_review", "human_review_required": True,
                  "reason_codes": ["conditions_or_undertakings_require_review"]}
        first = propose_review(None, review_observation(status="registered",
                                  conditions=("condition-A", "condition-B", "condition-C")), assess)
        reviewed = apply_review(first, "held", actor_ref="test:person", evidence_ref="test:record",
                                expected_version=1, reviewed_at_utc="2026-11-13T09:00:00Z")
        next_item = review_observation(status="registered", conditions=tuple(names), observation_id="o2")
        self.assertEqual(propose_review(reviewed, next_item, assess), reviewed)

    @settings(max_examples=40, deadline=None)
    @given(st.lists(st.text(min_size=1, max_size=15), min_size=1, max_size=8, unique=True))
    def test_second_watch_for_same_ref_cannot_increase_monitor_coverage(self, identifiers: list[str]) -> None:
        engagements = [{"engagementRef": f"test:e{i}", "watchRef": f"test:w{i}",
                        "facilityRef": "test:rural", "kind": "locum", "active": True}
                       for i in range(len(identifiers))]
        watches = [{"watchRef": f"test:w{i}", "registrationNumber": "TEST-" + name, "enabled": True}
                   for i, name in enumerate(identifiers)]
        original = assess_engagement_coverage(engagements, watches)
        watches.append({"watchRef": "test:w0", "registrationNumber": "TEST-NEW", "enabled": True})
        with_duplicate = assess_engagement_coverage(engagements, watches)
        self.assertLessEqual(with_duplicate["covered"], original["covered"])
        self.assertIn("test:e0", with_duplicate["ambiguous"])

    @settings(max_examples=40, deadline=None)
    @given(st.sampled_from(["limited", "provisional", "non_practising", "other", "unknown"]))
    def test_special_registration_categories_cannot_become_positive_practice_claim(self, category: str) -> None:
        item = qualified_observation()
        item["registrationDetail"]["categories"] = [category]
        result = assess_qualified(item, qualification=policy(), purpose="credentialing_read",
                                  now_utc="2026-11-13T09:00:00Z")
        self.assertTrue(result["human_review_required"])
        self.assertFalse(result["practice_authorised"])
        self.assertNotEqual(result["disposition"], "source_verified")


if __name__ == "__main__":
    unittest.main()
