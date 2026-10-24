import copy
import unittest

from scripts.f12_operator_inputs import build_operator_inputs, FIELDS, SELECTION_PARAMETER


def baseline():
    selector = "@parameters('" + SELECTION_PARAMETER + "')"
    return {'properties': {'connectionReferences': {'existing': {'source': 'Invoker'}},
        'definition': {'parameters': {SELECTION_PARAMETER: {'type': 'Object', 'defaultValue': {}},
                                    'baseline': {'type': 'Object', 'defaultValue': {}}},
            'triggers': {'manual': {'type': 'Request', 'kind': 'Button',
                'inputs': {'schema': {'type': 'object', 'properties': {}, 'required': []}}}},
            'actions': {'Parse_configuration': {'type': 'Scope', 'runAfter': {}, 'actions': {
                'Parse_selection': {'type': 'ParseJson', 'inputs': {'content': selector,
                    'schema': {'required': list(FIELDS), 'additionalProperties': False,
                               'properties': {k: {'type': 'string', 'minLength': 1} for k in FIELDS}}}},
                'Validate_dates': {'type': 'Compose', 'inputs': selector + "?['window_start']"}}},
                'Read_source': {'type': 'OpenApiConnection',
                    'runAfter': {'Parse_configuration': ['Succeeded']},
                    'inputs': {'parameters': {'query': selector + "?['subject']"}}},
                'Compare': {'type': 'Compose', 'inputs': {'all_checks': 21}}}}}}


class OperatorInputTests(unittest.TestCase):
    def test_form_uses_plain_controls_and_preserves_bindings_and_input(self):
        b = baseline(); original = copy.deepcopy(b); result = build_operator_inputs(b)
        self.assertEqual(b, original)
        self.assertEqual(result['properties']['connectionReferences'], b['properties']['connectionReferences'])
        d = result['properties']['definition']; schema = d['triggers']['manual']['inputs']['schema']
        self.assertEqual(set(schema['properties']), {'configuration_mode', *FIELDS})
        self.assertEqual(schema['properties']['configuration_mode']['default'], 'Saved configuration')
        self.assertEqual(d['parameters'], b['properties']['definition']['parameters'])

    def test_every_selector_consumer_uses_same_guarded_object(self):
        d = build_operator_inputs(baseline())['properties']['definition']; a = d['actions']
        for key in ('Parse_configuration', 'Read_source'):
            self.assertNotIn("parameters('" + SELECTION_PARAMETER + "')", repr(a[key]))
        self.assertEqual(a['Parse_configuration']['runAfter'], {'Operator_selection': ['Succeeded']})
        self.assertEqual(a['Compare'], baseline()['properties']['definition']['actions']['Compare'])
        self.assertEqual(a['Parse_configuration']['actions']['Parse_selection']['inputs']['schema'],
                         baseline()['properties']['definition']['actions']['Parse_configuration']['actions']['Parse_selection']['inputs']['schema'])
        mode = a['Operator_selection']['inputs']
        self.assertIn("empty(triggerBody()?['configuration_mode'])", mode)
        self.assertIn("parameters('" + SELECTION_PARAMETER + "')", mode)
        self.assertTrue(mode.endswith("outputs('Meeting_details'),json('{}')))"))
        for key in FIELDS:
            self.assertEqual(a['Meeting_details']['inputs'][key], "@coalesce(triggerBody()?['" + key + "'],'')")

    def test_unexpected_input_schema_cannot_be_silently_overwritten(self):
        b = baseline(); b['properties']['definition']['triggers']['manual']['inputs']['schema']['properties']['existing'] = {'type': 'string'}
        with self.assertRaises(ValueError):
            build_operator_inputs(b)


if __name__ == '__main__':
    unittest.main()
