"""Pure fictional tests for non-premium RIMS native handoff preflight."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/"rims_native_preflight.py"
spec=importlib.util.spec_from_file_location("rims_native_preflight",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NativePreflightTests(unittest.TestCase):
    def setUp(self):
        self.candidate={"subject_id":"synthetic-pub-01","assertion_type":"publication",
                        "evidence_hash":"synthetic-evidence","etag":'"5"'}
        self.proposal={"subject_id":"synthetic-pub-01","assertion_type":"publication",
                       "status":"ConfirmedCHHHS","decision_id":"synthetic-d1",
                       "candidate_hash":m.digest(self.candidate),
                       "evidence_hash":"synthetic-evidence",
                       "expected_etag":'"5"',"supersedes":None,
                       "reviewer_id":"fictional-reviewer",
                       "reason":"synthetic verification",
                       "decided_utc":"2026-11-10T00:00:00Z"}

    def test_requires_external_actor_check(self):
        with self.assertRaises(m.PreflightError):
            m.batch_preflight([self.candidate],[],[self.proposal])
        result=m.batch_preflight([self.candidate],[],[self.proposal],
                                  verify_actor=lambda decision,candidate: True)
        self.assertEqual(result["count"],1)
        self.assertFalse(result["write_authorised"])

    def test_batch_atomic_failure(self):
        second={**self.candidate,"subject_id":"synthetic-pub-02"}
        wrong={**self.proposal,"subject_id":"synthetic-pub-02","decision_id":"d2",
               "candidate_hash":m.digest(second),"expected_etag":'"4"'}
        with self.assertRaises(m.PreflightError):
            m.batch_preflight([self.candidate,second],[],[self.proposal,wrong],
                              verify_actor=lambda d,c:True)

    def test_reviewer_denial(self):
        with self.assertRaises(m.PreflightError):
            m.batch_preflight([self.candidate],[],[self.proposal],
                              verify_actor=lambda d,c:False)

    def test_supersession_must_match_latest(self):
        previous={**self.proposal}
        with self.assertRaises(m.PreflightError):
            m.batch_preflight([self.candidate],[previous],[self.proposal],
                              verify_actor=lambda d,c:True)
        changed={**self.proposal,"decision_id":"synthetic-d2","supersedes":"synthetic-d1"}
        result=m.batch_preflight([self.candidate],[previous],[changed],
                                  verify_actor=lambda d,c:True)
        self.assertEqual(result["count"],1)

    def test_historical_visiting_not_employee(self):
        rel={"person_id":"fictional-person","relationship_id":"r1",
             "organisation_id":"fictional-org","effective_from":"2021-01-01",
             "effective_to":"2023-12-31","relationship_kind":"Visiting",
             "evidence_hash":"synthetic-hash"}
        self.assertEqual(m.temporal_affiliations("fictional-person","2025-01-01",[rel]),[])
        active=m.temporal_affiliations("fictional-person","2022-01-01",[rel])
        self.assertFalse(active[0]["employment_confirmed"])

    def test_unverified_issue_denied(self):
        snapshot={"period":"2026-10","source_digest":"synthetic-source"}
        decisions=[{"subject_id":"fictional-p","assertion_type":"publication",
                    "status":"ConfirmedCHHHS","candidate_hash":"hash",
                    "decision_id":"fictional-d"}]
        with self.assertRaises(m.PreflightError):
            m.report_issue_preflight(snapshot,decisions)
        with self.assertRaises(m.PreflightError):
            m.report_issue_preflight(snapshot,decisions,verify_decision=lambda d:False)
        issued=m.report_issue_preflight(snapshot,decisions,verify_decision=lambda d:True)
        self.assertEqual(issued["approved_count"],1)
        self.assertFalse(issued["publication_authorised"])
        revised=m.report_issue_preflight(snapshot,[],verify_decision=lambda d:True,prior_issue=issued)
        self.assertTrue(revised["requires_reissue_review"])

    def test_employment_excluded_from_report(self):
        with self.assertRaises(m.PreflightError):
            m.report_issue_preflight({"period":"2026-10","source_digest":"source"},
                [{"subject_id":"p","assertion_type":"employment","status":"EmployeeConfirmed"}],
                verify_decision=lambda d:True)


if __name__=="__main__":
    unittest.main()
