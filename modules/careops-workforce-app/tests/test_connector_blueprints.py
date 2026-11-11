import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class BlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'flows'/'blueprints'/'sharepoint-cas-action-pair.json').read_text())

    def test_only_sharepoint_standard_connector(self):
        actions=self.data['actions']
        self.assertEqual(set(actions),{'Read_Head','CAS_Head'})
        for a in actions.values():
            self.assertEqual(a['inputs']['host']['operationId'],'HttpRequest')
            self.assertIn('shared_sharepointonline',a['inputs']['host']['apiId'])
            self.assertEqual(a['type'],'OpenApiConnection')

    def test_cas_uses_exact_dynamic_etag_not_wildcard(self):
        cas=self.data['actions']['CAS_Head']['inputs']['parameters']
        self.assertEqual(cas['parameters/method'],'POST')
        self.assertEqual(cas['parameters/headers']['X-HTTP-Method'],'MERGE')
        self.assertNotEqual(cas['parameters/headers']['IF-MATCH'],'*')
        self.assertIn('Read_Head',cas['parameters/headers']['IF-MATCH'])

    def test_no_literal_tenant_connection_or_user(self):
        raw=json.dumps(self.data)
        self.assertNotIn('.sharepoint.com',raw)
        self.assertNotIn('@example.com',raw)
        self.assertNotIn('Authorization',raw)
        self.assertEqual(self.data['status'],'unbound-template-disabled')

    def test_binding_and_stage_gates_documented(self):
        self.assertIn('trusted actor resolver',self.data['deployment_gates'])
        self.assertIn('SharePoint 412 and 429 tenant tests',self.data['deployment_gates'])
        self.assertIn('exact business version hash',self.data['deployment_gates'])
if __name__=='__main__':unittest.main()
