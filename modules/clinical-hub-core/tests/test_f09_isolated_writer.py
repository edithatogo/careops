import copy
import json
import unittest
from scripts.f09_isolated_writer import build_trial


class IsolatedWriterTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {'schemaVersion': '1.0', 'properties': {
            'connectionReferences': {}, 'definition': {
                'triggers': {'manual': {'inputs': {'schema': {}}}},
                'actions': {
                    'Fixed_Fictional_Cases': {'type': 'Compose', 'inputs': [], 'runAfter': {}},
                    'Initialize_Date_Results': {'type': 'InitializeVariable', 'inputs': {'variables': []}, 'runAfter': {'Fixed_Fictional_Cases': ['Succeeded']}},
                    'Validate_Case_Dates': {'type': 'Foreach', 'actions': {}, 'runAfter': {'Initialize_Date_Results': ['Succeeded']}},
                    'Evaluate_Claims': {'type': 'Select', 'inputs': {}, 'runAfter': {'Validate_Case_Dates': ['Succeeded']}},
                    'Outcome_Previews': {'type': 'Select', 'inputs': {}, 'runAfter': {'Evaluate_Claims': ['Succeeded']}},
                }}}}
        self.config = dict(site='https://example.invalid/test',
                           list_id='00000000-0000-0000-0000-000000000001',
                           description='Synthetic technical commissioning only. Fixture.',
                           entity_type='SP.Data.TestListItem', reference='test_sharepoint')

    def actions(self, d):
        out=[]
        def walk(x):
            if isinstance(x, dict):
                if x.get('type') == 'OpenApiConnection': out.append(x)
                for v in x.values(): walk(v)
            elif isinstance(x, list):
                for v in x: walk(v)
        walk(d)
        return out

    def test_only_fixture_rest_calls_and_one_write(self):
        d=build_trial(self.baseline, **self.config)
        calls=self.actions(d)
        self.assertEqual(sum(a['inputs']['parameters']['parameters/method']=='POST' for a in calls),1)
        for a in calls:
            p=a['inputs']['parameters']
            self.assertIn(self.config['list_id'],p['parameters/uri'])
            self.assertEqual(p['dataset'],self.config['site'])
            self.assertEqual(a['inputs']['retryPolicy'],{'type':'none'})
            self.assertEqual(a['inputs']['host']['operationId'],'HttpRequest')
            self.assertEqual(a['inputs']['authentication'],"@parameters('$authentication')")

    def test_no_input_controls_target_or_wording(self):
        d=build_trial(self.baseline, **self.config)
        schema=d['properties']['definition']['triggers']['manual']['inputs']['schema']
        self.assertEqual(set(schema['properties']),{'text'})
        self.assertFalse(schema['additionalProperties'])
        for a in self.actions(d):
            p=a['inputs']['parameters']
            self.assertNotIn('triggerBody',p['parameters/uri'])
            if 'parameters/body' in p:
                self.assertNotIn('triggerBody',p['parameters/body'])
                self.assertIn('FICTIONAL',p['parameters/body'])

    def test_legacy_semantics_retained_and_baseline_unmodified(self):
        before=copy.deepcopy(self.baseline)
        d=build_trial(self.baseline, **self.config)
        self.assertEqual(self.baseline,before)
        legacy=d['properties']['definition']['actions']['Commissioning_or_legacy_preview']['actions']
        for n in ['Fixed_Fictional_Cases','Evaluate_Claims','Outcome_Previews']:
            self.assertEqual(legacy[n],before['properties']['definition']['actions'][n])

    def test_drift_and_nonfictional_target_fail_before_build(self):
        self.baseline['properties']['connectionReferences']={'unexpected':{}}
        with self.assertRaises(ValueError):build_trial(self.baseline,**self.config)
        self.baseline['properties']['connectionReferences']={}
        self.config['description']='Live register'
        with self.assertRaises(ValueError):build_trial(self.baseline,**self.config)

    def test_reconciliation_checks_every_field_and_missing_review_no_calls(self):
        d=build_trial(self.baseline,**self.config)
        guard=d['properties']['definition']['actions']['Commissioning_or_legacy_preview']['else']['actions']['Explicit_fictional_review']
        self.assertEqual(self.actions(guard['else']),[])
        branch=guard['actions']['Fixture_identity_matches']['actions']['One_existing_operation']['actions']['Stored_operation_matches']
        for name in ('Title','OperationKey','SourceReference','SourceRevision','AuthorityReference','ReviewedWording','HistoryText'):
            self.assertIn(name,branch['expression'])
        self.assertEqual(self.actions(branch),[])
        revision=branch['actions']['Expected_revision_matches']['expression']
        self.assertIn("first(body('Read_fixture_operation')?['value'])?['SourceRevision']",revision)
        self.assertIn("'FICTIONAL-REV2','FICTIONAL-REV1'",revision)
        self.assertNotIn("@not(equals(triggerBody()",revision)



class ResourceBindingTests(unittest.TestCase):
    def setUp(self):
        from scripts.f09_isolated_writer import bindings_from_workspace
        self.resolve = bindings_from_workspace
        self.guid = '00000000-0000-0000-0000-000000000001'
        native = dict(Id=self.guid, EnableVersioning=True, EnableAttachments=False,
                      OnQuickLaunch=False, Description='Synthetic technical commissioning only. Fixture.',
                      RootFolder={'ServerRelativeUrl':'/sites/test/Lists/F09 test'})
        self.workspace = {
            'feature_control':{'active_feature':'F09-reviewed-outcome-commit'},
            'target':{'site_url':'https://example.invalid/sites/test'},
            'assets':[{'key':'f09_commissioning_fixture',  # gitleaks:allow -- fixture asset label, not a credential
                       'status':'found','resource_id':self.guid,
                       'url':'https://example.invalid/sites/test/Lists/F09%20test/AllItems.aspx'}],
            'runtime_readbacks':{'f09_isolated_fixture_created_20261011':{
                'result':{'list':{'status':200,'data':native}},
                'creation_identity':{'id':self.guid,'list_item_entity_type':'SP.Data.F09TestListItem'}}}}
        self.binding = dict(statecode=0,connectionid='fixture-existing',
                            connectorid='/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                            connectionreferencelogicalname='fixture_reference')

    def test_resource_bindings_resolve_without_guessing_entity_type(self):
        cfg=self.resolve(self.workspace,self.binding)
        self.assertEqual(cfg['list_id'],self.guid)
        self.assertEqual(cfg['entity_type'],'SP.Data.F09TestListItem')
        self.assertEqual(cfg['reference'],'fixture_reference')

    def test_resource_bindings_reject_wrong_identity_or_site(self):
        for mutation in ('id','host','path'):
            with self.subTest(mutation=mutation):
                w=copy.deepcopy(self.workspace)
                if mutation=='id':w['assets'][0]['resource_id']='00000000-0000-0000-0000-000000000002'
                elif mutation=='host':w['target']['site_url']='https://other.invalid/sites/test'
                else:w['assets'][0]['url']='https://example.invalid/sites/test/Lists/Other/AllItems.aspx'
                with self.assertRaises(ValueError):self.resolve(w,self.binding)

    def test_resource_bindings_reject_inactive_or_wrong_connector(self):
        for key,value in [('statecode',1),('connectorid','other'),('connectionid','')]:
            with self.subTest(key=key):
                b=dict(self.binding);b[key]=value
                with self.assertRaises(ValueError):self.resolve(self.workspace,b)

    def test_resource_bindings_reject_changed_defaults_and_unknown_entity(self):
        for key,value in [('EnableVersioning',False),('EnableAttachments',True),('OnQuickLaunch',True)]:
            w=copy.deepcopy(self.workspace)
            w['runtime_readbacks']['f09_isolated_fixture_created_20261011']['result']['list']['data'][key]=value
            with self.assertRaises(ValueError):self.resolve(w,self.binding)
        self.workspace['runtime_readbacks']['f09_isolated_fixture_created_20261011']['creation_identity']['list_item_entity_type']='guessed-from-title'
        with self.assertRaises(ValueError):self.resolve(self.workspace,self.binding)

    def test_resource_bindings_cli_preserves_candidate_and_private_boundary(self):
        import pathlib
        import subprocess
        import sys
        import tempfile
        helper=IsolatedWriterTests()
        helper.setUp()
        with tempfile.TemporaryDirectory() as temporary:
            root=pathlib.Path(temporary)
            ops=root/'private'/'ops'; ops.mkdir(parents=True)
            working=root/'private'/'working'; working.mkdir()
            wp=ops/'workspace.json';wp.write_text(json.dumps(self.workspace))
            bp=working/'baseline.json';bp.write_text(json.dumps({'clientdata':json.dumps(helper.baseline)}))
            rp=working/'binding.json';rp.write_text(json.dumps(self.binding))
            out=working/'candidate.json'
            command=[sys.executable,str(pathlib.Path('scripts/f09_isolated_writer.py').resolve()),
                     '--workspace',str(wp),'--baseline',str(bp),'--binding',str(rp),'--output',str(out)]
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            saved=out.read_bytes()
            repeat=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(repeat.returncode,0)
            self.assertEqual(out.read_bytes(),saved)
            command[-1]=str(root/'public-candidate.json')
            forbidden=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(forbidden.returncode,0)
            self.assertFalse((root/'public-candidate.json').exists())

if __name__=='__main__':unittest.main()
