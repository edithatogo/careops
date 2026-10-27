"""Offline contract and generated-worker safety checks. SPDX-License-Identifier: Apache-2.0"""
import copy
import unittest
from scripts.correspondence_planner_automation import (
    build, eligible, snapshot_patch, waiting_start, field_specs, view_specs,
)
from scripts.correspondence_linked_action import build as manual_build, PLANNER, SHAREPOINT


def config():
    return dict(site_url='https://fictional-example.sharepoint.com/sites/executive',
                register_list_id='11111111-1111-4111-8111-111111111111',
                tenant_id='22222222-2222-4222-8222-222222222222',
                planner_container_id='33333333-3333-4333-8333-333333333333',
                planner_plan_id='a'*28, planner_bucket_id='b'*28,
                planner_connection='fictional-planner', sharepoint_connection='fictional-sharepoint',
                record_form_url='https://fictional-example.sharepoint.com/sites/executive/Lists/Register/DispForm.aspx',
                open_progress=['In Progress', 'Awaiting further info'], waiting_progress='Awaiting further info')


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.item = dict(Id=4, CaptureState='Reviewed', Completed='In Progress',
                         PlannerActionRequired=True, PlannerActionTitle='Prepare response')

    def test_explicit_reviewed_open_action_only(self):
        self.assertTrue(eligible(self.item, config()))
        for patch in [{'CaptureState':'NeedsReview'}, {'Completed':'Completed'},
                      {'Completed':None}, {'Completed':'FYI'}, {'PlannerActionRequired':False},
                      {'PlannerActionRequired':'true'}, {'PlannerActionTitle':'   '},
                      {'PlannerActionTitle':'x'*121}, {'Id':0}]:
            with self.subTest(patch=patch):
                self.assertFalse(eligible({**self.item, **patch}, config()))

    def test_task_completion_only_changes_technical_snapshot(self):
        item = {**self.item, 'PlannerTaskState':'In progress', 'PlannerTaskCompletedAt':None,
                'Actions':'Human note', 'WaitingSince':'2026-10-01T00:00:00Z'}
        before = copy.deepcopy(item)
        task = {'id':'task', 'planId':'a'*28, 'percentComplete':100,
                'completedDateTime':'2026-10-27T00:00:00Z'}
        self.assertEqual(snapshot_patch(item, task), {
            'PlannerTaskState':'Completed', 'PlannerTaskCompletedAt':'2026-10-27T00:00:00Z'})
        self.assertEqual(item, before)

    def test_repeated_snapshot_is_noop_and_reopen_clears_current_date(self):
        task = {'percentComplete':100, 'completedDateTime':'2026-10-27T00:00:00Z'}
        item = {'PlannerTaskState':'Completed', 'PlannerTaskCompletedAt':task['completedDateTime']}
        self.assertEqual(snapshot_patch(item, task), {})
        self.assertEqual(snapshot_patch(item, {'percentComplete':25}),
                         {'PlannerTaskState':'In progress', 'PlannerTaskCompletedAt':None})

    def test_snapshot_mapping_cannot_target_correspondence_status(self):
        for name in ['Completed','completed','COMPLETED']:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    snapshot_patch({}, {'percentComplete':0}, {'task_state':name})

    def test_absent_or_bad_completion_never_completed(self):
        for task in [None, {}, {'percentComplete':101}, {'percentComplete':True},
                     {'percentComplete':100}, {'percentComplete':100,'completedDateTime':'not-a-date'}]:
            with self.subTest(task=task):
                patch=snapshot_patch({'PlannerTaskState':'Completed'}, task)
                self.assertEqual(patch.get('PlannerTaskState'), 'Unavailable')
                self.assertNotIn('Completed', patch)

    def test_waiting_transition_ignores_later_technical_versions(self):
        versions=[{'VersionId':2048,'VersionLabel':'4.0','Created':'2026-10-27T01:00:00Z','Completed':'Awaiting further info'},
                  {'VersionId':1536,'VersionLabel':'3.0','Created':'2026-10-20T00:00:00Z','Completed':'Awaiting further info'},
                  {'VersionId':1024,'VersionLabel':'2.0','Created':'2026-10-10T00:00:00Z','Completed':'In Progress'}]
        self.assertEqual(waiting_start(versions,'4.0','Awaiting further info',complete=False),
                         '2026-10-20T00:00:00Z')
        self.assertIsNone(waiting_start(versions,'5.0','Awaiting further info',complete=True))

    def test_missing_transition_requires_complete_history(self):
        versions=[{'VersionId':512,'VersionLabel':'1.0','Created':'2026-10-01T00:00:00Z','Completed':'Awaiting further info'}]
        self.assertIsNone(waiting_start(versions,'1.0','Awaiting further info',complete=False))
        self.assertEqual(waiting_start(versions,'1.0','Awaiting further info',complete=True), versions[0]['Created'])
        self.assertIsNone(waiting_start([], '1.0', 'Awaiting further info', complete=True))

    def test_out_of_order_or_naive_dates_do_not_invent_waiting_start(self):
        self.assertIsNone(waiting_start([{'VersionId':512,'VersionLabel':'1.0','Created':'2026-10-01T00:00:00','Completed':'Awaiting further info'}], '1.0','Awaiting further info',complete=True))

    def test_boolean_version_is_not_a_proven_history_identity(self):
        self.assertIsNone(waiting_start([{'VersionId':True,'VersionLabel':'1.0','Created':'2026-10-01T00:00:00Z','Completed':'Awaiting further info'}],'1.0','Awaiting further info',complete=True))


class WorkerTests(unittest.TestCase):
    def test_stopped_disabled_serial_recurrence(self):
        p=build(config())['properties'];d=p['definition']
        self.assertEqual(p['state'],'Stopped')
        self.assertFalse(d['parameters']['AutomationEnabled']['defaultValue'])
        self.assertEqual(d['triggers']['recurrence']['recurrence'],{'frequency':'Minute','interval':15})
        self.assertEqual(d['triggers']['recurrence']['runtimeConfiguration']['concurrency']['runs'],1)
        loops=[x for x in walk(d) if x.get('type')=='Foreach']
        self.assertEqual(len(loops),1)
        self.assertEqual(loops[0]['runtimeConfiguration']['concurrency']['repetitions'],1)
        for node in walk(d):
            if node.get('type')=='InitializeVariable':self.assertEqual(len(node['inputs']['variables']),1)

    def test_standard_operations_no_send_task_edit_or_direct_http(self):
        calls=[x['inputs'] for x in walk(build(config())) if x.get('type')=='OpenApiConnection']
        self.assertEqual({x['host']['apiId'] for x in calls},{PLANNER,SHAREPOINT})
        self.assertFalse(any(x.get('type') in {'Http','Workflow'} for x in walk(build(config()))))
        self.assertEqual(sum(x['host']['operationId']=='CreateTask_V3' for x in calls),1)
        for c in calls:
            self.assertEqual(c['retryPolicy'],{'type':'none'})
            if c['host']['apiId']==PLANNER:
                self.assertIn(c['host']['operationId'],{'ListTasks_V3','CreateTask_V3','GetTask_V2','GetTaskDetails_V2','UpdateTaskDetails_V2'})
                self.assertFalse(any(s in str(c['parameters']).lower() for s in ['assignment','duedatetime','comment','description']))

    def test_no_terminate_or_initialize_inside_loop(self):
        for node in walk(build(config())):
            if node.get('type') in {'Foreach','Until'}:
                self.assertFalse(any(x.get('type') in {'Terminate','InitializeVariable'} for x in walk(node['actions'])))

    def test_patch_field_allowlist_and_etag(self):
        graph=build(config());allowed={'PlannerActionKey','PlannerTaskId','PlannerTaskUrl','PlannerLinkState','PlannerTaskState','PlannerTaskCompletedAt','WaitingSince'}
        for node in walk(graph):
            if node.get('type')=='Compose' and isinstance(node.get('inputs'),dict):
                body=node['inputs']
                if any(k.startswith('Planner') or k=='WaitingSince' for k in body):
                    self.assertTrue(set(body)<=allowed)
            if node.get('type')=='OpenApiConnection' and node['inputs']['host']['apiId']==SHAREPOINT:
                p=node['inputs']['parameters']
                if p['parameters/method']=='POST':
                    self.assertEqual(p['parameters/headers']['X-HTTP-Method'],'MERGE')
                    self.assertIn('IF-MATCH',p['parameters/headers'])
                    self.assertNotEqual(p['parameters/headers']['IF-MATCH'],'*')

    def test_common_identity_protocol_and_manual_candidate_preserved(self):
        before=manual_build(config());worker=build(config())
        self.assertEqual(before,manual_build(config()))
        text=str(worker)
        for value in ['TASK_CREATE_UNCERTAIN','TASK_LINK_REQUIRES_RECONCILIATION','__metadata','Task_id','PlannerActionKey']:
            self.assertIn(value,text)
        self.assertNotIn("triggerBody()?['ItemId']",text)
        self.assertNotIn("triggerBody()?['ActionTitle']",text)
        self.assertIn('Read_versions',text)
        self.assertIn('VersionLabel',text)
        self.assertIn("@union(coalesce(body('Read_details')?['references']",text)
        self.assertIn('Waiting_ended_changed',text)
        self.assertIn('Waiting_unknown_changed',text)

    def test_sibling_dependencies_and_unique_action_names(self):
        names=[]
        for node in walk(build(config())):
            if 'actions' not in node or not isinstance(node['actions'],dict):continue
            names.extend(node['actions'])
            for action in node['actions'].values():
                self.assertTrue(set(action.get('runAfter',{}))<=set(node['actions']))
        self.assertEqual(len(names),len(set(names)))

    def test_pagination_and_failures_not_reported_healthy(self):
        text=str(build(config()))
        for value in ['@odata.nextLink','Max_pages','Batch_failed','Incomplete_scan','Next_page_scope','Record_failed']:
            self.assertIn(value,text)

    def test_parser_projects_numeric_status_and_uses_supported_secure_inputs(self):
        parsers=[x for x in walk(build(config())) if x.get('type')=='ParseJson' and 'percentComplete' in x['inputs'].get('schema',{}).get('properties',{})]
        self.assertEqual(len(parsers),1)
        self.assertEqual(set(parsers[0]['inputs']['content']),{'percentComplete'})
        self.assertEqual(parsers[0]['runtimeConfiguration']['secureData']['properties'],['inputs'])

    def test_schema_and_views_do_not_default_optin_or_use_modified_waiting(self):
        fields=field_specs();self.assertIn('<Default>0</Default>',fields['PlannerActionRequired'])
        self.assertTrue(all('Required="FALSE"' in xml for xml in fields.values()))
        views=view_specs(config())
        self.assertIn('WaitingSince',views['Waiting too long']['query'])
        self.assertNotIn('Modified',views['Waiting too long']['query'])
        self.assertIn('IsNull',views['Waiting date unknown']['query'])
        self.assertIn('Completed',views['Ready for closure review']['query'])

    def test_reject_unqualified_or_conflicting_bindings(self):
        for patch in [{'open_progress':[]},{'open_progress':['Completed']},
                      {'fields':{'state':'Completed'}},{'automation_fields':{'task_state':'Completed'}},
                      {'automation_fields':{'task_state':'completed'}},
                      {'automation_fields':{'task_state':'plannertaskid'}},
                      {'page_size':0},{'max_pages':1000},{'waiting_progress':'Unknown'},
                      {'version_dates_utc_qualified':'false'},
                      {'site_url':'http://fictional-example.sharepoint.com'}]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):build({**config(),**patch})
