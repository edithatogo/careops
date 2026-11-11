"""Property-style and concurrent transaction tests, with deterministic seeds."""
import concurrent.futures
import random
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal
from datetime import date, timedelta

from workflow_runtime import WorkforceRuntime, AccessDenied, InvalidState, StaleState, add_months


class ConcurrentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=str(Path(self.tmp.name)/'r.db')
        r=WorkforceRuntime(self.path)
        r.add_grant('person','practitioner','A','2026-01-01','2031-01-01')
        r.add_grant('approver','approver','A','2026-01-01','2031-01-01')
        r.add_grant('director','clinical_director','A','2026-01-01','2031-01-01')
        r.add_grant('hr','medical_workforce','A','2026-01-01','2031-01-01')
        r.create_plan('p','person','A')
        self.payload={'cycle_weeks':2,'contracted_fortnight_hours':'80',
                      'planned_hours':'80','cst_hours':'8','minimum_cst_fraction':'0.10',
                      'rule_ref':'synthetic','sessions':[]}

    def test_parallel_duplicate_submit_returns_same_revision(self):
        def go(_):return WorkforceRuntime(self.path).submit('p','person',self.payload,'same-id','2026-11-11')
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            results=list(pool.map(go,range(40)))
        self.assertEqual(len({x['case_id'] for x in results}),1)
        self.assertEqual(len(WorkforceRuntime(self.path).history('p','person','2026-11-11')),1)

    def test_parallel_distinct_submit_one_wins_without_lost_history(self):
        def go(n):
            try:return WorkforceRuntime(self.path).submit('p','person',self.payload,f'operation-{n}','2026-11-11')
            except InvalidState:return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(go,range(24)))
        self.assertEqual(sum(x is not None for x in results),1)
        self.assertEqual(len(WorkforceRuntime(self.path).history('p','person','2026-11-11')),1)

    def test_month_end_interval_property(self):
        rng=random.Random(9127)
        for _ in range(250):
            start=date(rng.randrange(2020,2045),rng.randrange(1,13),1)
            delta=rng.randrange(1,80)
            target=add_months(start,delta)
            self.assertEqual(target.month,(start.month-1+delta)%12+1)
            self.assertEqual(target.day,1)

    def test_policy_rule_overlap_is_rejected(self):
        r=WorkforceRuntime(self.path)
        r.add_review_rule('annual','A',12,'2026-01-01','2028-01-01',1)
        with self.assertRaises(InvalidState):
            r.add_review_rule('annual','A',6,'2027-01-01','2029-01-01',2)

    def test_replay_changed_actor_fails(self):
        r=WorkforceRuntime(self.path)
        r.submit('p','person',self.payload,'same','2026-11-11')
        with self.assertRaises(InvalidState):
            r.submit('p','other',self.payload,'same','2026-11-11')

    def test_date_boundaries_hold(self):
        r=WorkforceRuntime(self.path)
        with self.assertRaises(AccessDenied):
            r.submit('p','person',self.payload,'outside','2031-01-01')
        with self.assertRaises(InvalidState):
            r.add_review_rule('short','A',0,'2026-01-01','2028-01-01',1)

if __name__=='__main__':unittest.main()
