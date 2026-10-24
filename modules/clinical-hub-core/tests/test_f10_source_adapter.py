import json
import copy
import unittest

from scripts.f10_source_adapter import build_trial, build_changed_source_trial

BINDINGS = dict(site='https://example.invalid/sites/fictional',
                list_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
                description='Synthetic technical commissioning only. Fictional source fixture', row_id=7,
                reference='cr_sharedsharepointonline_fictional')
CLASSIFIER_NAMES = ('Evaluate_Supplied_Claims', 'Classify_For_Review',
                    'Proposed_Review_Items', 'Excluded_Review_Items', 'Blocking_Exceptions')


def fictional_baseline():
    """Seven-action baseline with a small but connected classifier graph."""
    actions = {
        'Fixed_Fictional_Cases': {'runAfter': {}, 'type': 'Compose',
                                  'inputs': [{'record_id': 'FIC-A', 'status': 'open'}]},
        'Evaluate_Supplied_Claims': {'runAfter': {'Fixed_Fictional_Cases': ['Succeeded']},
                                     'type': 'Select', 'inputs': {'from': "@outputs('Fixed_Fictional_Cases')",
                                     'select': {'input': '@item()', 'eligible': "@equals(item()?['status'],'open')"}}},
        'Classify_For_Review': {'runAfter': {'Evaluate_Supplied_Claims': ['Succeeded']},
                                'type': 'Select', 'inputs': {'from': "@body('Evaluate_Supplied_Claims')",
                                'select': {'case_id': "@item()?['input']?['record_id']",
                                           'lane': "@if(item()?['eligible'],'PROPOSED_REVIEW','EXCLUDED_REVIEW')",
                                           'source_snapshot': "@item()?['input']"}}},
        'Proposed_Review_Items': {'runAfter': {'Classify_For_Review': ['Succeeded']},
                                  'type': 'Query', 'inputs': {'from': "@body('Classify_For_Review')",
                                  'where': "@equals(item()?['lane'],'PROPOSED_REVIEW')"}},
        'Excluded_Review_Items': {'runAfter': {'Classify_For_Review': ['Succeeded']},
                                  'type': 'Query', 'inputs': {'from': "@body('Classify_For_Review')",
                                  'where': "@equals(item()?['lane'],'EXCLUDED_REVIEW')"}},
        'Blocking_Exceptions': {'runAfter': {'Classify_For_Review': ['Succeeded']},
                                'type': 'Query', 'inputs': {'from': "@body('Classify_For_Review')",
                                'where': "@equals(item()?['lane'],'BLOCKING_EXCEPTION')"}},
        'Review_Preview': {'runAfter': {'Proposed_Review_Items': ['Succeeded'],
                                        'Excluded_Review_Items': ['Succeeded'],
                                        'Blocking_Exceptions': ['Succeeded']},
                           'type': 'Compose', 'inputs': {'status': 'PROPOSAL_ONLY',
                           'all_cases': "@body('Classify_For_Review')",
                           'proposed_review': "@body('Proposed_Review_Items')",
                           'excluded_review': "@body('Excluded_Review_Items')",
                           'blocking_exceptions': "@body('Blocking_Exceptions')",
                           'register_updated': False, 'notified': False}},
    }
    return {'properties': {'connectionReferences': {}, 'definition': {
        'triggers': {'manual': {'type': 'Request', 'kind': 'Button',
                                'inputs': {'schema': {'type': 'object', 'properties': {}, 'required': []}}}},
        'actions': actions}}, 'schemaVersion': '1.0'}


def walk_actions(actions):
    for name, action in actions.items():
        yield name, action
        if isinstance(action.get('actions'), dict):
            yield from walk_actions(action['actions'])
        if isinstance(action.get('else'), dict):
            yield from walk_actions(action['else'].get('actions', {}))


class F10SourceAdapterTests(unittest.TestCase):
    def setUp(self):
        self.baseline = fictional_baseline()

    def build(self, **overrides):
        return build_trial(self.baseline, **(BINDINGS | overrides))

    def test_clone_is_read_only_and_classifier_graph_is_preserved(self):
        original = copy.deepcopy(self.baseline)
        result = self.build()
        self.assertEqual(self.baseline, original)
        self.assertIsNot(result, self.baseline)
        original_actions = self.baseline['properties']['definition']['actions']
        actions = result['properties']['definition']['actions']
        guard = actions['Fixture_identity_matches']['actions']
        self.assertEqual(guard['Read_snapshot']['inputs']['parameters']['parameters/method'], 'GET')
        self.assertEqual(guard['Source_qualified']['actions']['Fixed_Fictional_Cases']['inputs'],
                         "@json(body('Read_snapshot')?['SnapshotJson'])?['records']")
        classifier = guard['Source_qualified']['actions']
        for name in CLASSIFIER_NAMES:
            self.assertEqual(classifier[name], original_actions[name])
        self.assertEqual(classifier['Classify_For_Review']['inputs']['from'],
                         "@body('Evaluate_Supplied_Claims')")
        self.assertEqual(classifier['Proposed_Review_Items']['inputs']['from'],
                         "@body('Classify_For_Review')")
        self.assertEqual(classifier['Blocking_Exceptions']['inputs']['where'],
                         original_actions['Blocking_Exceptions']['inputs']['where'])
        self.assertEqual(actions['Read_fixture_identity']['inputs']['parameters']['parameters/method'], 'GET')

    def test_all_executable_external_calls_are_fixed_target_gets(self):
        actions = self.build()['properties']['definition']['actions']
        calls = [(name, action) for name, action in walk_actions(actions)
                 if action.get('type') == 'OpenApiConnection']
        self.assertEqual({name for name, _ in calls},
                         {'Read_fixture_identity', 'Read_snapshot', 'Read_snapshot_after_classification'})
        for _, action in calls:
            params = action['inputs']['parameters']
            self.assertEqual(params['parameters/method'], 'GET')
            self.assertEqual(params['dataset'], BINDINGS['site'])
            self.assertIn(BINDINGS['list_id'], params['parameters/uri'])
            self.assertEqual(action['inputs']['retryPolicy'], {'type': 'none'})
        self.assertNotIn('POST', repr(actions))
        self.assertNotIn('PATCH', repr(actions))
        self.assertNotIn('DELETE', repr(actions))

    def test_drift_checks_version_and_content_and_suppresses_preview(self):
        actions = self.build()['properties']['definition']['actions']
        source = actions['Fixture_identity_matches']['actions']['Source_qualified']['actions']
        gate = source['Review_Preview']
        self.assertIn("OData__UIVersionString", gate['expression'])
        self.assertIn("SnapshotJson", gate['expression'])
        self.assertIn('Stable_source_proposal', gate['actions'])
        refused = gate['else']['actions']['SOURCE_CHANGED_REFUSED']
        self.assertTrue(refused['inputs']['review_suppressed'])
        self.assertTrue(gate['runAfter'].get('Read_snapshot_after_classification'))
        self.assertEqual(source['Read_snapshot_after_classification']['runAfter'], {
            'Proposed_Review_Items': ['Succeeded'], 'Excluded_Review_Items': ['Succeeded'],
            'Blocking_Exceptions': ['Succeeded']})

    def test_invalid_bindings_are_rejected(self):
        for override in ({'site': 'http://example.com'}, {'list_id': 'not-a-guid'},
                         {'row_id': 0}, {'reference': ''}):
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.build(**override)

    def test_changed_source_simulation_mocks_only_second_read(self):
        observed = {'Id': 7, 'OperationKey': 'F10-COHERENT-SNAPSHOT1',
                    'SourceRevision': 'fictional-v7', 'OData__UIVersionString': '1.0',
                    'SnapshotJson': json.dumps({'synthetic_only': True})}
        before = copy.deepcopy(observed)
        result = build_changed_source_trial(self.baseline, observed_row=observed, **BINDINGS)
        self.assertEqual(observed, before)
        definition = result['properties']['definition']
        configured = [(name, a) for name, a in walk_actions(definition['actions'])
                      if 'staticResult' in a.get('runtimeConfiguration', {})]
        self.assertEqual([name for name, _ in configured], ['Read_snapshot_after_classification'])
        static = next(iter(definition['staticResults'].values()))['outputs']['body']
        self.assertEqual(static['OData__UIVersionString'], '2.0')
        self.assertEqual(static['SnapshotJson'], observed['SnapshotJson'])


if __name__ == '__main__':
    unittest.main()
