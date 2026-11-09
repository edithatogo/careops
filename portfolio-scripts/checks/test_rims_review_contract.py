"""Fictional RIMS adjudication contract regression tests."""
import unittest

from portfolio_scripts_rims_loader import load_contract

rims = load_contract()


class ReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {"subject_id": "fictional-doi:1", "assertion_type": "publication",
                          "evidence_hash": "synthetic-evidence-v1"}
        self.digest = rims.fingerprint(self.candidate)
        self.decision = {"schema": rims.SCHEMA, "decision_id": "d1",
                         "subject_id": self.candidate["subject_id"], "assertion_type": "publication",
                         "status": "ConfirmedCHHHS", "reviewer_id": "fictional-reviewer",
                         "decided_utc": "2026-11-10T00:00:00Z",
                         "evidence_hash": "synthetic-evidence-v1",
                         "candidate_hash": self.digest, "reason": "Fictional verified affiliation",
                         "supersedes": None}

    def test_confirmed_publication(self):
        d = rims.validate_decision(self.candidate, self.decision, expected_candidate_hash=self.digest)
        self.assertTrue(rims.may_publish(d))

    def test_pending_and_employee_not_publishable(self):
        for status in ("Uncertain", "NotCHHHS", "NeedsEvidence", "Duplicate"):
            self.assertFalse(rims.may_publish({**self.decision, "status": status}))
        self.assertFalse(rims.may_publish(None))
        self.assertFalse(rims.may_publish({**self.decision, "assertion_type": "employment", "status": "EmployeeConfirmed"}))

    def test_changed_candidate_refused(self):
        with self.assertRaises(rims.AdjudicationError):
            rims.validate_decision({**self.candidate, "evidence_hash": "changed"}, self.decision, expected_candidate_hash=self.digest)

    def test_reviewer_identity_required(self):
        with self.assertRaises(rims.AdjudicationError):
            rims.validate_decision(self.candidate, {**self.decision, "reviewer_id": ""}, expected_candidate_hash=self.digest)

    def test_supersession(self):
        updated = {**self.decision, "decision_id": "d2", "status": "NotCHHHS", "supersedes": "d1"}
        rims.validate_decision(self.candidate, updated, expected_candidate_hash=self.digest, previous=self.decision)
        with self.assertRaises(rims.AdjudicationError):
            rims.validate_decision(self.candidate, {**updated, "supersedes": "other"}, expected_candidate_hash=self.digest, previous=self.decision)

    def test_employee_effective_period(self):
        person = {"subject_id": "fictional-person:1", "assertion_type": "employment", "evidence_hash": "hr-redacted"}
        d = {**self.decision, "subject_id": person["subject_id"], "assertion_type": "employment",
             "status": "EmployeeConfirmed", "evidence_hash": "hr-redacted",
             "candidate_hash": rims.fingerprint(person)}
        with self.assertRaises(rims.AdjudicationError):
            rims.validate_decision(person, d, expected_candidate_hash=rims.fingerprint(person))
        person["effective_period"] = {"from": "2025-01-01", "to": None}
        d["candidate_hash"] = rims.fingerprint(person)
        rims.validate_decision(person, d, expected_candidate_hash=d["candidate_hash"])


if __name__ == "__main__":
    unittest.main()
