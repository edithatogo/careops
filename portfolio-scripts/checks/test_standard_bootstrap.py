# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Fictional bootstrap boundary and preservation checks; no tenant access."""
import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path
from defusedxml.ElementTree import fromstring

SCRIPT = Path(__file__).resolve().parents[1] / 'standard_bootstrap.py'
SPEC = importlib.util.spec_from_file_location('standard_bootstrap', SCRIPT)
BOOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOT)


class BootstrapTests(unittest.TestCase):
    def test_no_module_means_no_resources_or_tenant_actions(self):
        result = BOOT.compile_plan([])
        self.assertEqual(result['siteScript']['actions'], [])
        self.assertEqual(result['inventory']['resources'], [])
        self.assertEqual(result['plan']['nativeExecution'], 'not-executed')

    def test_catalogue_is_deterministic_and_complete_for_admitted_columns(self):
        first = BOOT.compile_plan(['careops-catalogue'])
        self.assertEqual(first, BOOT.compile_plan(['careops-catalogue']))
        self.assertEqual(set(first['siteScript']), {'$schema', 'actions'})
        self.assertEqual({r['name'] for r in first['inventory']['resources']},
                         {'Catalogue_Datasets', 'Catalogue_Resources', 'Catalogue_Assets'})
        ids = []
        for action in first['siteScript']['actions']:
            self.assertIn(action['verb'], {'createSiteColumnXml', 'createContentType', 'createSPList'})
            if 'schemaXml' in action:
                ids.append(fromstring(action['schemaXml']).get('ID'))
            for sub in action.get('subactions', []):
                self.assertNotIn(sub['verb'], {'deleteSPField', 'removeContentType', 'triggerFlow'})
                if 'schemaXml' in sub:
                    node = fromstring(sub['schemaXml'])
                    ids.append(node.get('ID'))
                    self.assertNotEqual(node.get('Name'), 'Title')
        self.assertEqual(len(ids), len(set(ids)))
        expected = sum(len(r['fields']) for r in first['inventory']['resources']) - 2
        self.assertEqual(len(ids), expected)

    def test_unknown_or_duplicate_module_is_refused(self):
        for modules in (['premium'], ['careops-catalogue', 'careops-catalogue']):
            with self.assertRaises(ValueError):
                BOOT.compile_plan(modules)

    def test_observed_identity_type_and_choice_drift_are_refused(self):
        inventory = BOOT.compile_plan(['careops-catalogue'])['inventory']
        BOOT.compile_plan(['careops-catalogue'], existing=copy.deepcopy(inventory))
        for change in ({'id': 'different'}, {'type': 'Note'}, {'required': False}):
            changed = copy.deepcopy(inventory)
            changed['resources'][0]['fields'][0].update(change)
            with self.assertRaises(ValueError):
                BOOT.compile_plan(['careops-catalogue'], existing=changed)
        changed = copy.deepcopy(inventory)
        choice = next(f for f in changed['resources'][0]['fields'] if f['type'] == 'Choice')
        choice['options'].append('unexpected')
        with self.assertRaises(ValueError):
            BOOT.compile_plan(['careops-catalogue'], existing=changed)

    def test_duplicate_native_fields_and_resource_type_drift_are_refused(self):
        changed = BOOT.compile_plan(['careops-catalogue'])['inventory']
        changed['resources'][0]['fields'].append(changed['resources'][0]['fields'][0])
        with self.assertRaises(ValueError):
            BOOT.compile_plan(['careops-catalogue'], existing=changed)

    def test_shared_site_columns_and_content_types_require_readback(self):
        for scope in ('siteColumns', 'contentTypes'):
            inventory = BOOT.compile_plan(['careops-catalogue'])['inventory']
            inventory[scope][0]['id'] = 'conflicting-existing-identity'
            with self.assertRaises(ValueError):
                BOOT.compile_plan(['careops-catalogue'], existing=inventory)
            del inventory[scope]
            with self.assertRaises(ValueError):
                BOOT.compile_plan(['careops-catalogue'], existing=inventory)
        changed = BOOT.compile_plan(['careops-catalogue'])['inventory']
        changed['resources'][0]['templateType'] = 101
        with self.assertRaises(ValueError):
            BOOT.compile_plan(['careops-catalogue'], existing=changed)

    def test_xml_text_is_escaped_and_never_interpreted_as_markup(self):
        row, xml = BOOT.field('example', 'Example', {'name': 'State', 'type': 'Choice',
                              'options': ['a&b', '<Field Name="Injected"/>']}, set())
        parsed = fromstring(xml)
        self.assertEqual(len(list(parsed.iter('Field'))), 1)
        self.assertEqual([x.text for x in parsed.findall('CHOICES/CHOICE')], row['options'])

    def test_invalid_schema_is_not_silently_coerced(self):
        cases = [
            {'name': 'Bad/Name', 'type': 'Text'},
            {'name': 'Good', 'type': 'Lookup'},
            {'name': 'Good', 'type': 'Text', 'required': 'false'},
            {'name': 'Good', 'type': 'Choice', 'options': ['one'], 'default': 'two'},
            {'name': 'Good', 'type': 'Choice', 'options': ['one', 'one']},
            {'name': 'Good', 'type': 'Note', 'unique': True},
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                BOOT.field('example', 'Example', case, set())

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.json'
            path.write_text('{"resources": [], "resources": [1]}')
            with self.assertRaises(ValueError):
                BOOT.read_json(path)

    def test_dictionary_is_safe_for_spreadsheet_opening(self):
        inventory = {'resources': [{'name': 'Example', 'fields': [{
            'name': 'Title', 'type': 'Text', 'required': False, 'unique': False,
            'indexed': False, 'options': ['=1+1'], 'default': '+1', 'id': 'fictional'}]}]}
        rendered = BOOT.csv_dictionary(inventory)
        self.assertIn("'=1+1", rendered)
        self.assertIn("'+1", rendered)


if __name__ == '__main__':
    unittest.main()
