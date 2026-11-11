# SPDX-License-Identifier: Apache-2.0
"""One scoped, read-only accreditation assurance packet across existing sources."""
import copy
import json
import unittest
from pathlib import Path

from scripts.ppg_assurance_bundle import assemble_bundle

ROOT = Path(__file__).parents[1]


class AssuranceBundleTests(unittest.TestCase):
    def setUp(self):
        self.graph=json.loads(
            (ROOT/"tests/fixtures/accreditation/second-example.json").read_text()
        )["graph"]

    def bundle(self, **kwargs):
        return assemble_bundle(
            self.graph, profiles=[], adoptions=[], receipts=[],
            context_key="ctx1", scope_key="scope1",
            as_of="2026-11-11", kinds=("action","quality-statement"), **kwargs)

    def test_missing_data_produces_review_candidates_not_compliance(self):
        result=self.bundle()
        self.assertEqual(result["contractVersion"],1)
        self.assertTrue(result["candidateReviewTasks"])
        self.assertTrue(all(t["state"]=="candidate-only" for t in result["candidateReviewTasks"]))
        self.assertFalse(result["tasksCreated"])
        self.assertFalse(result["complianceCertified"])
        self.assertIsNone(result["externalAccreditationDecision"])
        self.assertEqual(result["nativeWrites"],0)

    def test_source_and_evidence_projections_share_exact_graph_hash(self):
        original=copy.deepcopy(self.graph)
        result=self.bundle()
        digests={result["graphSha256"],result["coverage"]["graphSha256"],
                 result["obligations"]["graphSha256"],result["currency"]["graphSha256"]}
        self.assertEqual(len(digests),1)
        self.assertEqual(self.graph,original)

    def test_review_candidates_have_scoped_exact_ids(self):
        result=self.bundle()
        assert result["candidateReviewTasks"]
        for row in result["candidateReviewTasks"]:
            self.assertEqual(row["ReviewContextKey"],"ctx1")
            self.assertEqual(row["ScopeKey"],"scope1")
            self.assertTrue(row["RequirementKey"])
            self.assertIn(row["reason"],{
                "applicability-unresolved","assessment-missing",
                "evidence-source-unverified","mapping-review-pending",
                "local-adoption-unobserved"})

    def test_stable_output_order_without_raw_policy_body(self):
        self.assertEqual(self.bundle(),self.bundle())
        result=json.dumps(self.bundle())
        self.assertNotIn("Fictional policy describes a practice",result)

    def test_unknown_framework_without_source_profile_stays_unverified(self):
        result=self.bundle()
        self.assertTrue(all(x["normativeForce"]=="unverified"
                            for x in result["obligations"]["requirements"]))
        self.assertFalse(result["sourceAuthorityVerified"])

    def test_future_dated_review_refuses_consistently(self):
        with self.assertRaises(ValueError):
            self.bundle(as_of="not-a-date")


if __name__=="__main__":
    unittest.main()
