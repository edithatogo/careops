"""Tenant-free fictional end-to-end RIMS review workflow tests."""
import json
import tempfile
from pathlib import Path
import unittest

from portfolio_scripts_rims_loader import load_contract

# Import source file using explicit path; no packaging/tenant requirements.
from importlib.util import spec_from_file_location, module_from_spec
script = Path(__file__).resolve().parents[1] / "rims_review_queue.py"
spec = spec_from_file_location("rims_review_queue", script)
review = module_from_spec(spec)
spec.loader.exec_module(review)
contract = load_contract()


class ReviewQueueTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {"subject_id": "doi:10.0000/synthetic", "assertion_type": "publication",
                          "evidence_hash": "fictional-snapshot-hash", "source_id": "pubmed:42",
                          "title": "Fictional report"}
        self.decision = {"schema": contract.SCHEMA, "decision_id": "d1",
                         "subject_id": self.candidate["subject_id"], "assertion_type": "publication",
                         "status": "ConfirmedCHHHS", "reviewer_id": "fictional-authorised-actor",
                         "decided_utc": "2026-11-10T00:00:00Z",
                         "evidence_hash": self.candidate["evidence_hash"],
                         "candidate_hash": contract.fingerprint(self.candidate),
                         "reason": "Synthetic source evidence reviewed", "supersedes": None}

    def test_pending_by_default(self):
        out = review.evaluate([self.candidate], [])
        self.assertEqual(out["review_queue"][0]["review_state"], "NeedsReview")
        self.assertEqual(out["approved_publications"], [])

    def test_untrusted_offline_decision_is_not_a_publish_authority(self):
        out = review.evaluate([self.candidate], [self.decision])
        self.assertEqual(out["review_queue"][0]["review_state"], "ConfirmedCHHHS")
        self.assertEqual(out["approved_publications"], [])
        verified = review.evaluate([self.candidate], [self.decision], trusted_decisions=True)
        self.assertEqual(len(verified["approved_publications"]), 1)

    def test_source_revision_holds_old_decision(self):
        changed = {**self.candidate, "title": "Revised source claim"}
        out = review.evaluate([changed], [self.decision], trusted_decisions=True)
        self.assertEqual(out["review_queue"][0]["review_state"], "NeedsReview")
        self.assertEqual(len(out["stale_decisions"]), 1)
        self.assertEqual(out["approved_publications"], [])

    def test_reversal_supersedes_earlier_approval(self):
        later = {**self.decision, "decision_id": "d2", "status": "NotCHHHS", "supersedes": "d1"}
        out = review.evaluate([self.candidate], [self.decision, later], trusted_decisions=True)
        self.assertEqual(out["approved_publications"], [])
        self.assertEqual(out["review_queue"][0]["decision_id"], "d2")

    def test_duplicate_and_missing_subject_fail_closed(self):
        with self.assertRaises(review.QueueError):
            review.evaluate([self.candidate, self.candidate], [])
        with self.assertRaises(review.QueueError):
            review.evaluate([], [self.decision])

    def test_ambiguous_person_distinct_from_publication(self):
        person = {"subject_id": "person:synthetic", "assertion_type": "employment",
                  "evidence_hash": "fictional-hr-hash", "effective_period": {"from": "2025-01-01", "to": None}}
        decision = {**self.decision, "subject_id": person["subject_id"], "assertion_type": "employment",
                    "status": "EmployeeConfirmed", "decision_id": "e1", "evidence_hash": person["evidence_hash"],
                    "candidate_hash": contract.fingerprint(person)}
        out = review.evaluate([self.candidate, person], [decision], trusted_decisions=True)
        self.assertEqual(out["approved_publications"], [])

    def test_rejects_false_reviewers(self):
        with self.assertRaises(review.QueueError):
            review.evaluate([self.candidate], [{**self.decision, "reviewer_id": ""}])

    def test_csv_escapes_spreadsheet_formula(self):
        rows = review.evaluate([{**self.candidate, "title": "=HYPERLINK(fake)"}], [])["review_queue"]
        self.assertIn("'=HYPERLINK(fake)", review._csv_rows(rows))

    def test_cli_refuses_unknown_schema(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "input.json"
            p.write_text(json.dumps({"schema": "wrong", "candidates": [], "decisions": []}), encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                review.main([str(p)])
            self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
