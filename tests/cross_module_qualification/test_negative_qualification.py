"""Independent negative qualification tests across registration and MJP interfaces.

All inputs are fictional. These tests deliberately do not import either module's
private test helpers or mutate production/module source.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
REG_SRC = ROOT / "modules" / "careops-registration-assurance" / "src"
MJP_SRC = ROOT / "modules" / "careops-medical-job-planning"
sys.path.insert(0, str(REG_SRC))
sys.path.insert(0, str(MJP_SRC))

from registration_assurance.qualification import Qualification, assess_qualified  # noqa: E402
from careops_mjp_policy_rules import RulePack, assess_cst, RuleError  # noqa: E402
from careops_mjp_plan_records import PlanVersion, read_as_of, VersionError  # noqa: E402
from careops_mjp_negotiation import (  # noqa: E402
    NegotiationEvent, Thread, advance, NegotiationError,
)
from careops_mjp_cas_contract import (  # noqa: E402
    MemoryProtocolStore, SubmitCommand, submit_candidate, CandidateReceipt,
)

# Load MJP modules by file path: the module intentionally has no package wrapper.
import importlib.util


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Rebind the file-path modules under stable test-local aliases.
policy = load_module("careops_mjp_policy_rules", MJP_SRC / "policy_rules.py")
records = load_module("careops_mjp_plan_records", MJP_SRC / "plan_records.py")
negotiation = load_module("careops_mjp_negotiation", MJP_SRC / "negotiation.py")
cas = load_module("careops_mjp_cas_contract", MJP_SRC / "cas_contract.py")
RulePack, assess_cst, RuleError = policy.RulePack, policy.assess_cst, policy.RuleError
PlanVersion, read_as_of, VersionError = records.PlanVersion, records.read_as_of, records.VersionError
NegotiationEvent, Thread, advance, NegotiationError = (
    negotiation.NegotiationEvent, negotiation.Thread, negotiation.advance, negotiation.NegotiationError
)
MemoryProtocolStore, SubmitCommand, submit_candidate, CandidateReceipt = (
    cas.MemoryProtocolStore, cas.SubmitCommand, cas.submit_candidate, cas.CandidateReceipt
)

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "synthetic-cases.json").read_text())
NOW = FIXTURE["as_of_utc"]


def qualification(**changes):
    values = dict(FIXTURE["qualification"])
    values.update(changes)
    return Qualification(**values)


def observation(**changes):
    value = deepcopy(FIXTURE["observation"])
    for key, item in changes.items():
        value[key] = item
    return value


class RegistrationFailureQualificationTests(unittest.TestCase):
    def assess(self, obs=None, qual=None, purpose="test:registration-assurance"):
        return assess_qualified(
            obs or observation(), qualification=qual if qual is not None else qualification(),
            purpose=purpose, now_utc=NOW,
        )

    def test_missing_qualification_fails_closed(self):
        result = assess_qualified(observation(), qualification=None,
                                  purpose="test:registration-assurance", now_utc=NOW)
        self.assertEqual(result["disposition"], "unqualified_source")
        self.assertFalse(result["practice_authorised"])

    def test_disabled_qualification_fails_closed(self):
        result = self.assess(qual=qualification(enabled=False))
        self.assertEqual(result["disposition"], "unqualified_source")

    def test_unapproved_purpose_fails_closed(self):
        result = self.assess(purpose="test:employment-decision")
        self.assertEqual(result["reason_codes"], ["purpose_not_permitted"])

    def test_provider_identity_mismatch_fails_closed(self):
        result = self.assess(obs=observation(provider={
            "kind": "AHPRA_PIE_FIND", "qualificationRef": "test:other",
            "evidenceCeiling": "qualified_regulatory"
        }))
        self.assertEqual(result["reason_codes"], ["source_qualification_mismatch"])

    def test_provider_outage_never_reuses_old_positive_signal(self):
        result = self.assess(obs=observation(sourceHealth="blocked"))
        self.assertEqual(result["disposition"], "source_unavailable")
        self.assertFalse(result["practice_authorised"])

    def test_stale_source_is_not_current(self):
        obs = observation(evidence={"sourceRef": "test:old", "asOfUtc": "2026-11-12T00:00:00Z"})
        result = self.assess(obs=obs)
        self.assertEqual(result["disposition"], "stale_source")

    def test_future_source_timestamp_is_held(self):
        obs = observation(evidence={"sourceRef": "test:future", "asOfUtc": "2026-11-14T01:00:00Z"})
        result = self.assess(obs=obs)
        self.assertEqual(result["disposition"], "temporal_conflict")

    def test_legacy_schema_cannot_claim_current_positive_status(self):
        result = self.assess(obs=observation(schemaVersion="1.0.0"))
        self.assertEqual(result["disposition"], "verification_required")

    def test_unapproved_status_vocabulary_is_held(self):
        detail = deepcopy(FIXTURE["observation"]["registrationDetail"])
        detail["sourceVocabularyVersion"] = "test:unreviewed-vocabulary"
        result = self.assess(obs=observation(registrationDetail=detail))
        self.assertEqual(result["disposition"], "unqualified_source")

    def test_missing_native_status_or_category_is_held(self):
        detail = deepcopy(FIXTURE["observation"]["registrationDetail"])
        detail["categories"] = []
        result = self.assess(obs=observation(registrationDetail=detail))
        self.assertEqual(result["disposition"], "verification_required")

    def test_adverse_status_only_creates_review_candidate(self):
        signal = deepcopy(FIXTURE["observation"]["signal"])
        signal["registrationStatus"] = "suspended"
        result = self.assess(obs=observation(signal=signal))
        self.assertEqual(result["disposition"], "potential_adverse_change")
        self.assertTrue(result["human_review_required"])
        self.assertFalse(result["practice_authorised"])

    def test_restrictions_require_human_review(self):
        detail = deepcopy(FIXTURE["observation"]["registrationDetail"])
        detail["restrictions"] = ["test:restriction"]
        result = self.assess(obs=observation(registrationDetail=detail))
        self.assertEqual(result["disposition"], "restriction_review")
        self.assertFalse(result["practice_authorised"])


class MedicalJobPlanningAuthorityBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.as_of = date(2026, 11, 14)
        self.observed = datetime(2026, 11, 14, tzinfo=timezone.utc)

    def rule_pack(self, status="reference_only", adoption_ref=None):
        return RulePack(
            rule_key="test:cst-rule", edition="test:edition-1",
            source_ref="test:policy-source", source_sha256="a" * 64,
            clause_ref="test:clause-1", effective_from=date(2026, 1, 1),
            effective_to=None, status=status, adoption_ref=adoption_ref,
            eligible_classifications=frozenset({"test:classification"}),
            fraction=Decimal("0.1"),
        )

    def test_unverified_contract_never_establishes_eligibility(self):
        result = assess_cst(self.rule_pack(), classification="test:classification",
                            as_of=self.as_of, contracted_hours="80",
                            planned_hours="8", observed_hours=None, verified_contract=False)
        self.assertEqual(result["eligibility"], "source_unverified")
        self.assertFalse(result["approval_allowed"])
        self.assertFalse(result["rules_operative"])

    def test_reference_rule_is_not_operative_or_approvable(self):
        result = assess_cst(self.rule_pack(), classification="test:classification",
                            as_of=self.as_of, contracted_hours="80",
                            planned_hours="8", observed_hours="7", verified_contract=True)
        self.assertFalse(result["rules_operative"])
        self.assertFalse(result["approval_allowed"])
        self.assertEqual(result["interpretation"], "candidate_rule_not_industrial_determination")

    def test_even_adopted_candidate_rule_cannot_approve(self):
        result = assess_cst(self.rule_pack("adopted", "test:adoption-receipt"),
                            classification="test:classification", as_of=self.as_of,
                            contracted_hours="80", planned_hours="8",
                            observed_hours="8", verified_contract=True)
        self.assertTrue(result["rules_operative"])
        self.assertFalse(result["approval_allowed"])

    def test_superseded_or_retired_plan_without_end_date_is_rejected(self):
        with self.assertRaises(VersionError):
            PlanVersion(
                plan_ref="test:plan", version_ref="test:version",
                submitted_sha256="b" * 64, policy_snapshot_ref="test:policy",
                appointment_ref="test:appointment", position_ref="test:position",
                service_assignment_ref="test:service", effective_from=self.as_of,
                effective_to=None, issued_at=self.observed,
                decision_evidence_ref="test:decision", state="superseded",
            )

    def test_candidate_issued_projection_never_verifies_authority(self):
        version = PlanVersion(
            plan_ref="test:plan", version_ref="test:version",
            submitted_sha256="b" * 64, policy_snapshot_ref="test:policy",
            appointment_ref="test:appointment", position_ref="test:position",
            service_assignment_ref="test:service", effective_from=date(2026, 1, 1),
            effective_to=None, issued_at=self.observed,
            decision_evidence_ref="test:decision", state="issued",
        )
        result = read_as_of([version], plan_ref="test:plan", date_as_of=self.as_of,
                            observed_at=self.observed, source_read_complete=True)
        self.assertEqual(result["status"], "candidate_issued")
        self.assertFalse(result["authority_verified"])

    def test_incomplete_plan_source_is_never_treated_as_no_plan(self):
        result = read_as_of([], plan_ref="test:plan", date_as_of=self.as_of,
                            observed_at=self.observed, source_read_complete=False)
        self.assertEqual(result["status"], "unverified_incomplete_source")
        self.assertFalse(result["authority_verified"])

    def test_negotiation_cannot_skip_to_approval_or_issuance(self):
        initial = Thread("test:plan", "test:version", "c" * 64, 0, "submitted", ())
        with self.assertRaises(NegotiationError):
            event = NegotiationEvent("test:op", "approve", "test:actor", "test:role",
                                     "test:evidence", "d" * 64, self.observed)
            advance(initial, event, 0)

    def test_negotiation_stops_at_authority_pending_and_role_is_not_authentication(self):
        initial = Thread("test:plan", "test:version", "c" * 64, 0, "submitted", ())
        first = NegotiationEvent("test:op-1", "propose", "test:actor", "test:role",
                                 "test:evidence", "d" * 64, self.observed)
        consulting = advance(initial, first, 0)
        consensus = NegotiationEvent("test:op-2", "record_consensus", "test:actor",
                                     "test:role", "test:evidence", "e" * 64, self.observed)
        agreed = advance(consulting, consensus, 1)
        request = NegotiationEvent("test:op-3", "request_authorisation", "test:actor",
                                   "test:role", "test:evidence", "f" * 64, self.observed)
        pending = advance(agreed, request, 2)
        self.assertEqual(pending.state, "authority_pending")
        with self.assertRaises(NegotiationError):
            advance(pending, NegotiationEvent("test:op-4", "approve", "test:actor",
                   "test:role", "test:evidence", "1" * 64, self.observed), 3)

    def test_candidate_submission_receipt_is_not_approval(self):
        store = MemoryProtocolStore()
        command = SubmitCommand(
            plan_ref="test:plan", version_ref="test:version",
            operation_ref="test:operation", expected_generation=0,
            actor_evidence_ref="test:actor-evidence", payload={"hours": "8"},
        )
        receipt = submit_candidate(store, command)
        self.assertIsInstance(receipt, CandidateReceipt)
        self.assertEqual(receipt.outcome, "candidate_submitted")
        self.assertEqual(store.get_head("test:plan").state, "candidate_submitted")
        self.assertNotIn("approved", receipt.outcome)


if __name__ == "__main__":
    unittest.main()
