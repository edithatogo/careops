"""Synthetic-only RIMS assurance tests."""
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parents[1]/"rims_assurance.py"
spec=importlib.util.spec_from_file_location("rims_assurance",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AssuranceTests(unittest.TestCase):
    def test_identifier_collision_is_review_not_merge(self):
        records=[{"subject_id":"a","doi":"https://doi.org/10.1234/ABC"},
                 {"subject_id":"b","doi":"10.1234/abc"}]
        matches=m.candidate_matches(records)
        self.assertEqual(matches[0]["subjects"],["a","b"])
        self.assertEqual(matches[0]["resolution"],"human_required")

    def test_bad_identifier_refused(self):
        with self.assertRaises(m.AssuranceError):
            m.canonical_ids({"doi":"not a DOI"})

    def test_worklist_metadata_only(self):
        rows=[{"subject_id":"p1","assertion_type":"publication","review_state":"NeedsReview",
               "observed_utc":"2026-10-01T00:00:00Z","private_hr_record":"must not leak"}]
        result=m.worklist(rows,now_utc="2026-11-10T00:00:00Z")
        self.assertEqual(result[0]["lane"],"Overdue")
        self.assertNotIn("private_hr_record",str(result))

    def test_report_counts_and_reissue(self):
        source=[{"subject_id":"p1"},{"subject_id":"p2"}]
        review=[{"subject_id":"p1","review_state":"ConfirmedCHHHS"}]
        untrusted=m.report_reconciliation(source,review,period="2026-10")
        self.assertEqual(untrusted["approved_count"],0)
        self.assertEqual(untrusted["source_claimed_approved_count"],1)
        result=m.report_reconciliation(
            source,review,period="2026-10",
            verify_review=lambda key,record,decision: True)
        self.assertEqual((result["approved_count"],result["pending_count"]),(1,1))
        changed=m.report_reconciliation(source,[{"subject_id":"p1","review_state":"NotCHHHS"}],
                                        period="2026-10",prior_issue=result)
        self.assertTrue(changed["reissue_review_required"])
        self.assertEqual(changed["approved_count"],0)

    def test_unverified_exclusion_does_not_remove_publication(self):
        sources=[{"subject_id":"synthetic"}]
        unreviewed=[{"subject_id":"synthetic","review_state":"NotCHHHS"}]
        held=m.report_reconciliation(sources,unreviewed,period="2026-10")
        self.assertEqual(held["excluded_count"],0)
        self.assertEqual(held["pending_count"],1)
        self.assertEqual(held["reviewed_count"],0)
        self.assertEqual(held["source_review_status_count"],1)
        approved=m.report_reconciliation(
            sources,unreviewed,period="2026-10",
            verify_review=lambda key, source, decision: True,
        )
        self.assertEqual(approved["excluded_count"],1)
        self.assertEqual(approved["reviewed_count"],1)

    def test_orphan_review_refused(self):
        with self.assertRaises(m.AssuranceError):
            m.report_reconciliation([], [{"subject_id":"missing"}],period="2026-10")

    def test_receipt_summary_redacts_inputs(self):
        x=m.run_receipts([{"run_id":"synthetic-1","status":"partial",
            "finished_utc":"2026-11-09T00:00:00Z","url":"private"}],now_utc="2026-11-10T00:00:00Z")
        self.assertEqual(x["outcomes"]["partial"],1)
        self.assertNotIn("private",str(x))

if __name__=="__main__":
    unittest.main()
