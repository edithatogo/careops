# SPDX-License-Identifier: Apache-2.0
"""Fictional evidence currency tests; status is not proof of compliance."""
import copy
import json
from pathlib import Path
import unittest

from scripts.ppg_evidence_currency import project_currency

ROOT=Path(__file__).parents[1]


class EvidenceCurrencyTests(unittest.TestCase):
    def setUp(self):
        self.graph=json.loads(
            (ROOT/"tests/fixtures/accreditation/second-example.json").read_text()
        )["graph"]
        self.receipts=[
            {"EvidenceVersionKey":"ev1", "SourceSystem":"fictional-ppg",
             "SourceKey":"fixture-policy", "SourceVersion":"1",
             "CaptureRef":"fictional:capture:ev1", "ObservedOn":"2026-10-01",
             "ReviewDueOn":"2026-12-01","SourceSHA256":"a"*64},
        ]

    def project(self, receipts=None, **kwargs):
        return project_currency(
            self.graph, self.receipts if receipts is None else receipts,
            "ctx1", "scope1", as_of="2026-11-11", **kwargs)

    def test_exact_version_and_review_window_without_compliance_inference(self):
        prior=copy.deepcopy((self.graph,self.receipts))
        result=self.project()
        a=next(x for x in result["evidence"] if x["EvidenceVersionKey"]=="ev1")
        self.assertEqual(a["reviewWindow"],"within-review-window")
        self.assertEqual(a["sourceVersion"],"1")
        self.assertFalse(a["sourceBytesVerified"])
        self.assertIsNone(a["accreditationStatus"])
        self.assertEqual(result["nativeWrites"],0)
        self.assertEqual((self.graph,self.receipts),prior)

    def test_missing_receipt_unknown_instead_of_current(self):
        result=self.project(receipts=[])
        self.assertTrue(result["evidence"])
        self.assertTrue(all(x["reviewWindow"]=="unknown" for x in result["evidence"]))
        self.assertFalse(result["sourceAuthorityVerified"])

    def test_expired_evidence_requires_human_followup_not_bad_rating(self):
        self.receipts[0]["ReviewDueOn"]="2026-10-31"
        result=self.project()
        a=next(x for x in result["evidence"] if x["EvidenceVersionKey"]=="ev1")
        self.assertEqual(a["reviewWindow"],"review-due")
        self.assertEqual(a["followup"],"source-review-required")
        self.assertIsNone(a["accreditationStatus"])

    def test_unset_due_date_remains_unknown(self):
        self.receipts[0]["ReviewDueOn"]=None
        a=next(x for x in self.project()["evidence"]
               if x["EvidenceVersionKey"]=="ev1")
        self.assertEqual(a["reviewWindow"],"due-date-unset")

    def test_mismatched_evidence_version_identity_refused(self):
        for field,value in (("SourceSystem","other"),("SourceVersion","2"),
                            ("SourceKey","other")):
            with self.subTest(field=field):
                bad=copy.deepcopy(self.receipts)
                bad[0][field]=value
                with self.assertRaisesRegex(ValueError,"source identity"):
                    self.project(receipts=bad)

    def test_duplicate_and_unknown_receipts_refused(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            self.project(receipts=self.receipts+self.receipts)
        bad=copy.deepcopy(self.receipts)
        bad[0]["EvidenceVersionKey"]="not-found"
        with self.assertRaisesRegex(ValueError,"evidence version"):
            self.project(receipts=bad)

    def test_invalid_time_and_hash_rejected(self):
        for field,value in (("SourceSHA256","abc"),("ObservedOn","2028-01-01"),
                            ("ReviewDueOn","2026-01-01")):
            with self.subTest(field=field):
                bad=copy.deepcopy(self.receipts)
                bad[0][field]=value
                with self.assertRaises(ValueError):
                    self.project(receipts=bad)

    def test_result_order_independent_and_contains_no_policy_body(self):
        first=self.project()
        later=self.project(receipts=list(reversed(self.receipts)))
        self.assertEqual(first,later)
        self.assertNotIn("Fictional policy describes a practice",json.dumps(first))

    def test_scope_rejection(self):
        with self.assertRaisesRegex(ValueError,"scope"):
            project_currency(self.graph,self.receipts,"ctx1","scope2",as_of="2026-11-11")

if __name__=="__main__":
    unittest.main()
