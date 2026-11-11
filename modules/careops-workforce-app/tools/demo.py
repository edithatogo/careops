"""Completely synthetic local pathway demonstration, no real CHHHS data."""
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timezone, timedelta, date
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'sharepoint')]
from sharepoint_adapter import Adapter,SqliteSharePointSimulator,Principal
from flow_state import start_case,decide,DecisionContext
from domain import next_review_date,obligation_key,diff_versions

def run():
 with TemporaryDirectory() as temp:
  store=SqliteSharePointSimulator(str(Path(temp)/'synthetic.db'))
  engine=Adapter(store);engine.bootstrap('fake-plan-001','doctor@example.invalid','fictional-service')
  officer=Principal('doctor@example.invalid',frozenset({'practitioner:fictional-service'}))
  approver=Principal('employer@example.invalid',frozenset({'approver:fictional-service'}))
  first=engine.submit('fake-plan-001',officer,'fake-revision-01',{'hours':80,'cycle_weeks':2},'submit-001',0)
  now=datetime(2026,11,11,tzinfo=timezone.utc)
  case=start_case('fake-case','fake-revision-01',first['pending']['digest'],officer.subject,'fictional-service')
  stages=[('clinical_director','clinical@example.invalid'),('clinical_director','clinical@example.invalid'),('medical_workforce','workforce@example.invalid'),('approver',approver.subject)]
  for index,(role,subject) in enumerate(stages):
   ctx=DecisionContext(subject,role,'fictional-service',now+timedelta(days=10),officer.subject,role=='approver')
   case=decide(case,ctx,'approve',f'approve-stage-{index}',index,now)
  if case['status']!='approved':raise AssertionError('approval stages incomplete')
  approved=engine.decide('fake-plan-001',approver,'approve','finalise-001',1,'2026-12-01')
  active=engine.activate('fake-plan-001',approver,'activate-001',2,'2026-12-01')
  due=engine.review_obligation('fake-plan-001',approver,'annual',1,'2027-12-01')
  return {'plan':active['plan_id'],'active':active['current'],'history':engine.history('fake-plan-001',officer),
          'review_obligation_key':due['key'],'four_stage_decision_count':len(case['decisions']),
          'actor_type':'fictional only','native_tenant_qualified':False}
if __name__=='__main__':print(json.dumps(run(),indent=2))
