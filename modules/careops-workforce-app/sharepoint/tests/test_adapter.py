import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from sharepoint_adapter import (Adapter, SqliteSharePointSimulator, Conflict, Forbidden,
                                InvalidTransition, AmbiguousOperation, InjectedCrash,
                                canonical_digest, Principal)

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=str(Path(self.tmp.name)/'sp.db')
        self.db=SqliteSharePointSimulator(self.path)
        self.a=Adapter(self.db)
        self.a.bootstrap('p','doctor','renal')
        self.doctor=Principal('doctor',frozenset({'practitioner:renal'}))
        self.manager=Principal('manager',frozenset({'approver:renal'}))

    def submit(self):
        return self.a.submit('p',self.doctor,'v1',{'hours':80},'submit',0)

    def test_durable_replay_after_restart(self):
        first=self.submit()
        resumed=Adapter(SqliteSharePointSimulator(self.path))
        self.assertEqual(first,resumed.submit('p',self.doctor,'v1',{'hours':80},'submit',0))
        self.assertEqual(len(self.db.list_artifacts('p')),1)

    def test_same_id_changed_payload_is_denied(self):
        self.submit()
        with self.assertRaises(AmbiguousOperation):
            self.a.submit('p',self.doctor,'v1',{'hours':72},'submit',0)

    def test_stale_generation_fails(self):
        self.submit()
        with self.assertRaises(Conflict):
            self.a.submit('p',self.doctor,'v2',{'hours':72},'other',0)

    def test_self_approval_and_cross_service_rejected(self):
        self.submit()
        with self.assertRaises(Forbidden):
            self.a.decide('p',self.doctor,'approve','denied',1,'2099-01-01')
        with self.assertRaises(Forbidden):
            self.a.decide('p',Principal('external',frozenset({'approver:other'})),
                          'approve','denied2',1,'2099-01-01')

    def test_future_effective_approval_activation(self):
        self.submit()
        self.a.decide('p',self.manager,'approve','decision',1,'2099-01-01')
        self.assertIsNone(self.a.read('p',self.doctor)['current'])
        with self.assertRaises(InvalidTransition):
            self.a.activate('p',self.manager,'tooearly',2,'2098-12-31')
        self.assertEqual(self.a.activate('p',self.manager,'activate',2,'2099-01-01')['current'],'v1')
        self.assertEqual(self.a.history('p',self.doctor),['v1'])

    def test_crash_between_cas_and_receipt_recovers(self):
        with self.assertRaises(InjectedCrash):
            self.a.submit('p',self.doctor,'v1',{'hours':80},'submit',0,crash_after_cas=True)
        resumed=Adapter(SqliteSharePointSimulator(self.path))
        self.assertEqual(resumed.submit('p',self.doctor,'v1',{'hours':80},'submit',0)['generation'],1)
        self.assertEqual(resumed.operation('submit')['status'],'committed')

    def test_prepared_receipt_and_staged_artifact_replayed(self):
        digest=canonical_digest({'hours':80})
        fingerprint=canonical_digest({'operation':'submit','principal':'doctor','plan_id':'p',
                             'request':{'command':'submit','version_id':'v1','digest':digest},'expected':0})
        self.db.create_unique('operations','submit',{'key':'submit','plan_id':'p','digest':fingerprint,'status':'prepared'})
        self.db.create_unique('artifacts','submit',{'type':'version','version_id':'v1','digest':digest,
                    'content':{'hours':80},'plan_id':'p','transaction_key':'submit'})
        self.submit()
        self.assertEqual(len(self.db.list_artifacts('p')),1)

    def test_staged_orphan_not_approved_history(self):
        self.db.create_unique('artifacts','orphan',{'plan_id':'p','version_id':'orphan'})
        self.assertEqual(self.a.history('p',self.doctor),[])

    def test_review_obligation_deduplicates_across_restart(self):
        first=self.a.review_obligation('p',self.manager,'annual',1,'2027-01-01')
        again=Adapter(SqliteSharePointSimulator(self.path)).review_obligation(
                        'p',self.manager,'annual',1,'2027-01-01')
        self.assertEqual(first,again)
        self.assertNotEqual(first['key'],self.a.review_obligation('p',self.manager,'annual',2,'2028-01-01')['key'])

    def test_prior_approved_version_remains_during_next_submission(self):
        self.submit()
        self.a.decide('p',self.manager,'approve','decision',1,'2099-01-01')
        self.a.activate('p',self.manager,'activate',2,'2099-01-01')
        self.a.submit('p',self.doctor,'v2',{'hours':72},'new',3)
        self.assertEqual(self.a.read('p',self.doctor)['current'],'v1')

    def test_no_wildcard_etag_or_invalid_numeric_snapshot(self):
        with self.assertRaises(Conflict): self.db.cas('heads','p','*',{})
        with self.assertRaises(ValueError): canonical_digest({'bad':float('nan')})

if __name__=='__main__':unittest.main()
