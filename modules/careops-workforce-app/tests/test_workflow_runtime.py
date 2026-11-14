"""Synthetic, offline tests of transactional workforce job-plan lifecycle."""
import tempfile
import unittest
from datetime import date
from pathlib import Path

from workflow_runtime import WorkforceRuntime, AccessDenied, InvalidState, StaleState


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = str(Path(self.temp.name) / 'workforce.sqlite3')
        self.r = WorkforceRuntime(self.db)
        self.r.add_grant('clinician', 'practitioner', 'svc', '2026-01-01', '2029-01-01')
        self.r.add_grant('director', 'clinical_director', 'svc', '2026-01-01', '2029-01-01')
        self.r.add_grant('hr', 'medical_workforce', 'svc', '2026-01-01', '2029-01-01')
        self.r.add_grant('delegate', 'approver', 'svc', '2026-01-01', '2029-01-01')
        self.r.add_grant('director', 'practitioner', 'svc', '2026-01-01', '2029-01-01')
        self.r.create_plan('p1', 'clinician', 'svc')
        self.r.create_plan('p2', 'director', 'svc')
        self.now = '2026-11-11'
        self.plan = {'cycle_weeks': 2, 'contracted_fortnight_hours': '80', 'planned_hours': '80', 'cst_hours': '8', 'sessions': [], 'rule_ref': 'synthetic-rule-1', 'minimum_cst_fraction': '0.10'}

    def submitted(self, plan='p1', user='clinician', operation='submit1'):
        return self.r.submit(plan, user, self.plan, operation, self.now)

    def decide_all(self, case_id, effective='2026-11-15'):
        self.r.decide(case_id, 'director', 'approve', 'd1', self.now)
        self.r.decide(case_id, 'director', 'approve', 'd2', self.now)
        self.r.decide(case_id, 'hr', 'approve', 'd3', self.now)
        return self.r.decide(case_id, 'delegate', 'approve', 'd4', self.now, effective)

    def test_unbalanced_hours_fail_before_version_creation(self):
        bad={**self.plan,'planned_hours':'79'}
        with self.assertRaises(InvalidState):
            self.r.submit('p1','clinician',bad,'unbalanced',self.now)
        self.assertEqual(self.r.history('p1','clinician',self.now),[])

    def test_unversioned_or_underprotected_time_fails_closed(self):
        for bad in ({**self.plan,'rule_ref':''}, {**self.plan,'cst_hours':'3'},
                    {**self.plan,'contracted_fortnight_hours':'NaN'}):
            with self.subTest(bad=bad),self.assertRaises(InvalidState):
                self.r.submit('p1','clinician',bad,'invalid-'+str(len(str(bad))),self.now)

    def test_submit_replay_across_restart(self):
        a = self.submitted()
        self.assertEqual(self.r.submit('p1', 'clinician', self.plan, 'submit1', self.now), a)
        self.assertEqual(WorkforceRuntime(self.db).submit('p1','clinician',self.plan,'submit1',self.now), a)
        with self.assertRaises(InvalidState):
            self.r.submit('p1','clinician',{'hours': 3},'submit1',self.now)

    def test_multi_stage_approval_and_future_activation(self):
        c=self.submitted()['case_id']
        self.decide_all(c)
        self.assertIsNone(self.r.practitioner_dashboard('clinician',self.now)['plans'][0]['active_version'])
        self.assertEqual(self.r.activate_due('2026-11-14'),0)
        self.assertEqual(self.r.activate_due('2026-11-15'),1)
        self.assertEqual(self.r.activate_due('2026-11-15'),0)
        first=self.r.history('p1','clinician',self.now)
        self.assertEqual(len(first),1)
        self.assertEqual(first[0]['status'],'active')
        b=self.submitted(operation='submit2')
        self.assertEqual(self.r.practitioner_dashboard('clinician',self.now)['plans'][0]['active_version'],first[0]['version_id'])
        self.assertEqual(len(self.r.history('p1','clinician',self.now)),2)
        self.assertEqual(b['status'],'submitted')

    def test_delegation_and_self_approval_fail_closed(self):
        c=self.submitted()['case_id']
        for subject in ['clinician','delegate','hr']:
            with self.subTest(subject=subject),self.assertRaises(AccessDenied):
                self.r.decide(c,subject,'approve','unauth'+subject,self.now)
        mycase=self.submitted('p2','director','s2')['case_id']
        with self.assertRaises(AccessDenied):
            self.r.decide(mycase,'director','approve','own',self.now)

    def test_return_and_new_revision_preserve_candidate(self):
        c=self.submitted()['case_id']
        self.r.decide(c,'director','return','ret1',self.now)
        self.assertEqual(self.r.get_case(c,'clinician',self.now)['status'],'returned')
        with self.assertRaises(InvalidState):
            self.r.decide(c,'director','approve','ret2',self.now)
        self.submitted(operation='submit2')
        self.assertEqual(len(self.r.history('p1','clinician',self.now)),2)

    def test_policy_edition_review_schedule_and_no_change_attestation(self):
        self.r.add_review_rule('annual','svc',12,'2026-01-01','2027-01-01',1)
        self.r.add_review_rule('annual','svc',6,'2027-01-01','2030-01-01',2)
        self.assertEqual(self.r.sweep_reviews('2026-12-01'),0)
        self.assertEqual(self.r.sweep_reviews('2027-01-02'),2)
        self.assertEqual(self.r.sweep_reviews('2027-01-02'),0)
        obligations=self.r.approver_dashboard('delegate','2027-01-02')['obligations']
        self.assertEqual(len(obligations),2)
        self.assertEqual({o['rule_edition'] for o in obligations},{1})
        self.r.attest_no_change('p1','delegate','annual','2027-01-01','attest1','2027-01-02')
        self.assertEqual(self.r.attest_no_change('p1','delegate','annual','2027-01-01','attest1','2027-01-02')['status'],'complete')
        self.assertEqual(len(self.r.history('p1','clinician','2027-01-02')),0)

    def test_dashboards_two_roles_and_history_access(self):
        self.submitted('p1')
        self.submitted('p2','director','other')
        dual=self.r.available_workspaces('director',self.now)
        self.assertEqual(dual,['approver','practitioner'])
        self.assertEqual(self.r.available_workspaces('clinician',self.now),['practitioner'])
        self.assertEqual(len(self.r.approver_dashboard('director',self.now)['cases']),1)
        with self.assertRaises(AccessDenied):
            self.r.history('p2','clinician',self.now)
        with self.assertRaises(AccessDenied):
            self.r.approver_dashboard('clinician',self.now)

    def test_generation_and_expired_authority(self):
        case=self.submitted()['case_id']
        with self.assertRaises(StaleState):
            self.r.decide(case,'director','approve','stale',self.now,expected_generation=9)
        with self.assertRaises(AccessDenied):
            self.r.decide(case,'director','approve','expired','2029-01-02')

    def test_disputed_or_rejected_cannot_activate(self):
        case=self.submitted()['case_id']
        self.r.decide(case,'director','reject','rej1',self.now)
        self.assertEqual(self.r.activate_due('2026-12-31'),0)
        self.assertEqual(self.r.get_case(case,'clinician',self.now)['status'],'rejected')

if __name__=='__main__':unittest.main()
