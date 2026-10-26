"""Critical action write boundaries, offline. SPDX-License-Identifier: Apache-2.0"""
import unittest
from scripts.correspondence_linked_action import build,PLANNER,SHAREPOINT

def fixture():
 return dict(site_url='https://fictional-example.sharepoint.com/sites/executive',register_list_id='11111111-1111-4111-8111-111111111111',tenant_id='22222222-2222-4222-8222-222222222222',planner_container_id='33333333-3333-4333-8333-333333333333',planner_plan_id='a'*28,planner_bucket_id='b'*28,planner_connection='fictional-planner',sharepoint_connection='fictional-sharepoint',record_form_url='https://fictional-example.sharepoint.com/sites/executive/Lists/Register/DispForm.aspx')
def walk(x):
 if isinstance(x,dict):
  yield x
  for y in x.values():yield from walk(y)
 elif isinstance(x,list):
  for y in x:yield from walk(y)
class LinkedActionTests(unittest.TestCase):
 def test_disabled_explicit_manual_and_review_gate(self):
  p=build(fixture())['properties'];d=p['definition']
  self.assertEqual(p['state'],'Stopped');self.assertFalse(d['parameters']['LinkEnabled']['defaultValue'])
  t=d['triggers']['manual'];self.assertEqual(t['kind'],'Button');self.assertEqual(t['runtimeConfiguration']['concurrency']['runs'],1)
  self.assertEqual(set(t['inputs']['schema']['required']),{'ItemId','ActionTitle'})
  self.assertEqual(d['actions']['Reviewed_record']['expression'],"@equals(outputs('Item')?['CaptureState'],'Reviewed')")
 def test_standard_operations_and_no_notification_or_description_writes(self):
  calls=[x['inputs'] for x in walk(build(fixture())) if x.get('type')=='OpenApiConnection']
  self.assertEqual({x['host']['apiId'] for x in calls},{PLANNER,SHAREPOINT})
  for c in calls:
   self.assertEqual(c['retryPolicy'],{'type':'none'})
   if c['host']['apiId']==PLANNER:
    self.assertIn(c['host']['operationId'],{'ListTasks_V3','CreateTask_V3','GetTask_V2','GetTaskDetails_V2','UpdateTaskDetails_V2'})
    self.assertFalse(any(w in str(c['parameters']).lower() for w in ['assignment','duedatetime','comment','description']))
  self.assertEqual(sum(c['host']['operationId']=='CreateTask_V3' for c in calls),1)
 def test_register_merges_only_link_fields_with_etag(self):
  graph=build(fixture());bodies=[x['inputs'] for x in walk(graph) if x.get('type')=='Compose' and isinstance(x.get('inputs'),dict)]
  self.assertTrue(bodies)
  for b in bodies:self.assertTrue(set(b)<={'PlannerActionKey','PlannerTaskId','PlannerTaskUrl','PlannerLinkState'})
  writes=[x['inputs']['parameters'] for x in walk(graph) if x.get('type')=='OpenApiConnection' and x['inputs']['host']['apiId']==SHAREPOINT and x['inputs']['parameters']['parameters/method']=='POST']
  self.assertEqual(len(writes),2)
  self.assertIn("lists(guid''11111111-1111-4111-8111-111111111111'')",str(graph))
  for p in writes:
   self.assertEqual(p['parameters/headers']['X-HTTP-Method'],'MERGE');self.assertIn('__metadata',p['parameters/headers']['IF-MATCH'])
 def test_pending_or_ambiguous_never_creates_again(self):
  d=build(fixture())['properties']['definition'];c=d['actions']['Task_route']['else']['actions']['Match_count']['else']['actions']['May_create']['expression']
  self.assertIn("equals(length(body('Filter_tasks')),0)",c)
  for f in ['PlannerLinkState','PlannerActionKey']:self.assertIn("empty(outputs('Item')?['"+f+"'])",c)
  self.assertIn('@odata.nextLink',d['actions']['Complete_plan_scan']['expression'])
 def test_scoped_dependencies_and_native_internal_name(self):
  d=build({**fixture(),'fields':{'key':'Planner_x0020_action_x0020_key'}})['properties']['definition'];self.assertIn('Planner_x0020_action_x0020_key',str(d));names=[]
  for x in walk({'actions':d['actions']}):
   if 'actions' in x:
    names.extend(x['actions'])
    for a in x['actions'].values():self.assertTrue(set(a.get('runAfter',{}))<=set(x['actions']))
  self.assertEqual(len(names),len(set(names)))
 def test_connector_backlinks_are_arrays_and_native_form_spaces_normalise(self):
  d=build({**fixture(),'record_form_url':fixture()['record_form_url'].replace('/Register/','/Test Register/')})['properties']['definition']
  self.assertIn('Test%20Register',d['actions']['Record_url']['inputs'])
  a=d['actions']['Have_task_id']['actions']
  self.assertIn("json('[]')",a['Existing_backlinks']['inputs']['from'])
  self.assertIn('resourceLink',a['Verified_backlinks']['inputs']['where'])
 def test_reject_bad_bindings(self):
  for change in [{'site_url':'http://example.org'},{'record_form_url':'https://other.example.org/item'},{'planner_connection':''},{'planner_plan_id':'not-a-plan'},{'fields':{'key':"unsafe')"}},{'register_list_id':'not-guid'}]:
   with self.assertRaises(ValueError):build({**fixture(),**change})
