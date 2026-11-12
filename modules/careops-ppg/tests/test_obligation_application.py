# SPDX-License-Identifier: Apache-2.0
"""Offline contract tests for publisher force and scoped policy adoption.

All examples use the already committed fictional accreditation graph. The
external source is a candidate unless the accountable publisher review is
recorded. This contract does not issue policies or accreditation decisions.
"""
import copy
import unittest
from pathlib import Path
import json

from scripts.ppg_obligation_application import project_obligations

ROOT = Path(__file__).parents[1]


class ObligationApplicationTests(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads(
            (ROOT / "tests/fixtures/accreditation/second-example.json").read_text()
        )["graph"]
        self.profiles = [{
            "FrameworkKey": "fixture-edition-1",
            "SourceKind": "external-directive",
            "NormativeForce": "unverified",
            "PublisherRef": "fixture:publisher",
            "CaptureKey": "fixture:capture",
            "ForceReview": None,
        }]
        self.adoptions = []

    def run_projection(self, *, as_of="2026-11-11"):
        return project_obligations(
            self.graph, self.profiles, self.adoptions,
            "ctx1", "scope1", as_of=as_of,
        )

    def test_unverified_force_and_absent_adoption_are_not_obligations(self):
        initial = copy.deepcopy((self.graph,self.profiles,self.adoptions))
        result = self.run_projection()
        action = next(x for x in result["requirements"]
                      if x["RequirementKey"] == "fixture-action")
        self.assertEqual(action["sourceKind"], "external-directive")
        self.assertEqual(action["normativeForce"], "unverified")
        self.assertEqual(action["localAdoption"], "unobserved")
        self.assertEqual(action["applicability"], "unknown")
        self.assertIsNone(action["complianceRating"])
        self.assertEqual((self.graph,self.profiles,self.adoptions),initial)
        self.assertEqual(result["nativeWrites"], 0)

    def test_reviewed_force_does_not_infer_application(self):
        self.profiles[0].update(
            NormativeForce="publisher-mandated",
            ForceReview={
                "ActorRef": "fictional:policy-reviewer",
                "DecisionRef": "fictional:review-1",
                "SourceLocator": "fictional page 1",
                "ReviewedAt": "2026-11-01",
            },
        )
        result=self.run_projection()
        selected=next(x for x in result["requirements"]
                      if x["RequirementKey"] == "fixture-action")
        self.assertEqual(selected["normativeForce"],"publisher-mandated")
        self.assertEqual(selected["applicability"],"unknown")
        self.assertIsNone(selected["complianceRating"])

    def test_publisher_force_requires_human_review(self):
        self.profiles[0]["NormativeForce"] = "publisher-mandated"
        with self.assertRaisesRegex(ValueError,"force review"):
            self.run_projection()

    def test_directive_cannot_be_silently_downgraded_to_guideline(self):
        self.profiles[0]["SourceKind"] = "external-guideline"
        self.profiles[0]["NormativeForce"] = "publisher-mandated"
        self.profiles[0]["ForceReview"] = {
            "ActorRef": "fictional:policy-reviewer", "DecisionRef": "fictional:review",
            "SourceLocator": "fictional source", "ReviewedAt": "2026-11-01",
        }
        with self.assertRaisesRegex(ValueError,"incompatible"):
            self.run_projection()

    def test_invalid_capture_not_accepted_as_source(self):
        self.profiles[0]["CaptureKey"] = "other-capture"
        with self.assertRaisesRegex(ValueError,"capture"):
            self.run_projection()

    def test_adopted_local_policy_requires_decision_and_exact_evidence_version(self):
        self.adoptions = [{
            "AdoptionKey":"adopt-1","EvidenceVersionKey":"ev1","ScopeKey":"scope1",
            "State":"adopted","EffectiveFrom":"2026-10-01","EffectiveTo":None,
            "DecisionRef":None,"ActorRef":None,"DecidedAt":None,
        }]
        with self.assertRaisesRegex(ValueError,"decision"):
            self.run_projection()
        self.adoptions[0].update(
            DecisionRef="fictional:approval",ActorRef="fictional:owner",
            DecidedAt="2026-09-30",
        )
        chosen=next(x for x in self.run_projection()["requirements"]
                    if x["RequirementKey"] == "fixture-action")
        self.assertEqual(chosen["localAdoption"],"adopted")
        self.assertIsNone(chosen["complianceRating"])

    def test_adoption_not_in_scope_or_wrong_evidence_version_refused(self):
        self.adoptions=[{
            "AdoptionKey":"adopt-1","EvidenceVersionKey":"nonexistent","ScopeKey":"scope1",
            "State":"proposed","EffectiveFrom":"2026-10-01","EffectiveTo":None,
        }]
        with self.assertRaisesRegex(ValueError,"evidence version"):
            self.run_projection()
        self.adoptions[0].update(EvidenceVersionKey="ev1", ScopeKey="scope2")
        with self.assertRaisesRegex(ValueError,"context scope"):
            self.run_projection()

    def test_future_or_expired_adoption_not_current(self):
        self.adoptions=[{
            "AdoptionKey":"adopt-1","EvidenceVersionKey":"ev1","ScopeKey":"scope1",
            "State":"adopted","EffectiveFrom":"2027-01-01","EffectiveTo":None,
            "DecisionRef":"fictional:approval","ActorRef":"fictional:owner",
            "DecidedAt":"2026-11-01",
        }]
        chosen=next(x for x in self.run_projection()["requirements"]
                    if x["RequirementKey"] == "fixture-action")
        self.assertEqual(chosen["localAdoption"],"scheduled")
        self.adoptions[0].update(EffectiveFrom="2026-01-01",
                                EffectiveTo="2026-10-01")
        chosen=next(x for x in self.run_projection()["requirements"]
                    if x["RequirementKey"] == "fixture-action")
        self.assertEqual(chosen["localAdoption"],"expired")

    def test_conflicting_simultaneous_adoptions_refused(self):
        self.adoptions=[{
            "AdoptionKey":"a1","EvidenceVersionKey":"ev1","ScopeKey":"scope1",
            "State":"adopted","EffectiveFrom":"2026-10-01","EffectiveTo":None,
            "DecisionRef":"fictional:approve","ActorRef":"fictional:owner",
            "DecidedAt":"2026-09-30",
        }]
        other=copy.deepcopy(self.adoptions[0])
        other.update(AdoptionKey="a2",DecisionRef="fictional:approve-2")
        self.adoptions.append(other)
        with self.assertRaisesRegex(ValueError,"conflicting adoption"):
            self.run_projection()

    def test_crosswalk_does_not_transfer_adoption(self):
        self.adoptions=[{
            "AdoptionKey":"adopt-1","EvidenceVersionKey":"ev1","ScopeKey":"scope1",
            "State":"adopted","EffectiveFrom":"2026-10-01","EffectiveTo":None,
            "DecisionRef":"fictional:approval","ActorRef":"fictional:owner",
            "DecidedAt":"2026-09-30",
        }]
        result=self.run_projection()
        self.assertFalse(result["acceptanceTransferred"])
        self.assertIsNone(result["externalAccreditationDecision"])

    def test_human_review_in_future_refused(self):
        self.profiles[0].update(NormativeForce="publisher-mandated", ForceReview={
            "ActorRef":"fictional:reviewer","DecisionRef":"fictional:review",
            "SourceLocator":"fictional page","ReviewedAt":"2027-01-01",
        })
        with self.assertRaisesRegex(ValueError,"future"):
            self.run_projection()


if __name__=="__main__":
    unittest.main()
