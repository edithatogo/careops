"""Synthetic contract checks for exact-row F09 amendment generation."""
import copy
import json
import unittest

from scripts.f09_isolated_writer import FIELDS, build_amendment_trial


def baseline_fixture():
    return {'schemaVersion': '1.0', 'properties': {'connectionReferences': {}, 'definition': {
        'triggers': {'manual': {'inputs': {'schema': {}}}}, 'actions': {
            'Fixed_Fictional_Cases': {'type': 'Compose', 'inputs': [], 'runAfter': {}},
            'Initialize_Date_Results': {'type': 'InitializeVariable', 'inputs': {'variables': []}, 'runAfter': {'Fixed_Fictional_Cases': ['Succeeded']}},
            'Validate_Case_Dates': {'type': 'Foreach', 'actions': {}, 'runAfter': {'Initialize_Date_Results': ['Succeeded']}},
            'Evaluate_Claims': {'type': 'Select', 'inputs': {}, 'runAfter': {'Validate_Case_Dates': ['Succeeded']}},
            'Outcome_Previews': {'type': 'Select', 'inputs': {}, 'runAfter': {'Evaluate_Claims': ['Succeeded']}},
        }}}}


class AmendmentWriterTests(unittest.TestCase):
    def setUp(self):
        self.baseline = baseline_fixture()
        self.config = dict(site='https://example.invalid/test',
            list_id='00000000-0000-0000-0000-000000000001',
            description='Synthetic technical commissioning only. Fixture.',
            entity_type='SP.Data.TestListItem', reference='test_sharepoint', row_id=1,
            before=dict(zip(FIELDS, ['FICTIONAL action title', 'F09-FICTIONAL-OP1',
                'FICTIONAL-MINUTES#P1', 'FICTIONAL-REV1', 'FICTIONAL-AUTH1',
                'Fictional reviewed wording v1', 'FICTIONAL-HISTORY1: retained.'])),
            after=dict(zip(FIELDS, ['FICTIONAL action title', 'F09-FICTIONAL-OP1',
                'FICTIONAL-MINUTES#P1', 'FICTIONAL-REV2', 'FICTIONAL-AUTH2',
                'Fictional reviewed wording v2', 'FICTIONAL-HISTORY1: retained. FICTIONAL-HISTORY2: amended.'])),
            original_etag='"{fixture-etag-1}"')

    def build(self, **overrides):
        return build_amendment_trial(self.baseline, **(self.config | overrides))

    @staticmethod
    def walk(value):
        if isinstance(value, dict):
            yield value
            for v in value.values():
                yield from AmendmentWriterTests.walk(v)
        elif isinstance(value, list):
            for v in value:
                yield from AmendmentWriterTests.walk(v)

    def calls(self, branch):
        return [x for x in self.walk(branch) if x.get('type') == 'OpenApiConnection']

    def test_contract_rejects_immutable_changes_and_incomplete_history(self):
        for field in ('Title', 'OperationKey', 'SourceReference'):
            after = dict(self.config['after']); after[field] += ' changed'
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.build(after=after)
        after = dict(self.config['after']); after['HistoryText'] = 'FICTIONAL-HISTORY-LOST'
        with self.assertRaises(ValueError): self.build(after=after)
        after = dict(self.config['after']); after['HistoryText'] = self.config['before']['HistoryText']
        with self.assertRaises(ValueError): self.build(after=after)
        with self.assertRaises(ValueError): self.build(original_etag='*')
        with self.assertRaises(ValueError): self.build(before={'Title': 'partial'})

    def test_baseline_is_unchanged_and_legacy_preview_survives(self):
        original = copy.deepcopy(self.baseline)
        candidate = self.build()
        self.assertEqual(self.baseline, original)
        legacy = candidate['properties']['definition']['actions']['Commissioning_or_legacy_preview']['actions']
        self.assertEqual(legacy['Outcome_Previews'], original['properties']['definition']['actions']['Outcome_Previews'])

    def test_fixed_target_and_amendment_payload_etags_and_retry_policy(self):
        candidate = self.build()
        definition = candidate['properties']['definition']
        actions = definition['actions']['Commissioning_or_legacy_preview']['else']['actions']['Explicit_fictional_review']['actions']
        identity = actions['Amendment_fixture_guard']['actions']
        calls = self.calls(identity)
        writes = [c for c in calls if c['inputs']['parameters']['parameters/method'] == 'POST']
        self.assertEqual(len(writes), 2)
        self.assertEqual(definition['triggers']['manual']['inputs']['schema']['properties']['text']['default'], 'amend')
        self.assertIn('items(1)', writes[0]['inputs']['parameters']['parameters/uri'])
        self.assertIn(self.config['list_id'], writes[0]['inputs']['parameters']['parameters/uri'])
        dynamic, stale = [w['inputs']['parameters'] for w in writes]
        self.assertEqual(dynamic['parameters/headers']['IF-MATCH'], "@body('Read_amendment_row')?['odata.etag']")
        self.assertEqual(stale['parameters/headers']['IF-MATCH'], self.config['original_etag'])
        expected_body = {'__metadata': {'type': self.config['entity_type']}, **self.config['after']}
        self.assertEqual(json.loads(dynamic['parameters/body']), expected_body)
        self.assertEqual(json.loads(stale['parameters/body']), expected_body)
        self.assertEqual(dynamic['parameters/headers']['Accept'], 'application/json;odata=minimalmetadata')
        self.assertIn('OData__UIVersionString', next(c for c in calls if c['inputs']['parameters']['parameters/method'] == 'GET')['inputs']['parameters']['parameters/uri'])
        self.assertTrue(all(c['inputs']['retryPolicy'] == {'type': 'none'} for c in calls))
        self.assertNotIn("IF-MATCH': '*'", repr(calls))

    def test_invalid_and_replay_routes_have_no_merge(self):
        candidate = self.build()
        cases = candidate['properties']['definition']['actions']['Commissioning_or_legacy_preview']['else']['actions']['Explicit_fictional_review']['actions']['Amendment_fixture_guard']['actions']['Exact_row_guard']['actions']['Select_case']['cases']
        for name in ('amend', 'stale_etag', 'replay'):
            self.assertEqual(name, cases[name]['case'])
        self.assertEqual(self.calls(cases['replay']), [])
        self.assertEqual(self.calls(cases['amend']['actions']['Before_state_guard']['else']), [])
        stale = cases['stale_etag']['actions']['After_state_guard']['actions']
        self.assertEqual(len([c for c in self.calls(stale) if c['inputs']['parameters']['parameters/method'] == 'POST']), 1)
        self.assertIn('STALE_ETAG_REFUSED', repr(stale))
        handler = stale['Classify_stale_etag_failure']
        self.assertEqual(handler['expression'], "@equals(outputs('Stale_etag_merge')?['statusCode'],412)")
        self.assertEqual(handler['else']['actions']['Unexpected_stale_failure_stop']['inputs']['runStatus'], 'Failed')
        self.assertIn('STALE_ETAG_UNEXPECTED_SUCCESS_STOP', repr(stale))


if __name__ == '__main__':
    unittest.main()
