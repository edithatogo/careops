import json
import ast
import re
import unittest
from scripts.f07_operator_inputs import build_operator_inputs, build_paper_preflight


def evaluate_generated(expression, inputs):
    """Evaluate the emitted scalar WDL subset; expected outcomes are independent."""
    expression = re.sub(r"triggerBody\(\)\?\['([^']+)'\]", lambda m: repr(inputs.get(m[1])), expression.lstrip('@'))
    for word in ('if', 'and', 'or', 'not'):
        expression = re.sub(r'\b' + word + r'\(', word + '_(', expression)
    functions = {'if_': lambda c,a,b: a if c else b, 'and_': lambda *v: all(v),
        'or_': lambda *v: any(v), 'not_': lambda v: not v, 'equals': lambda a,b: a == b,
        'coalesce': lambda *v: next((x for x in v if x is not None), None),
        'empty': lambda v: v is None or v == '' or v == [], 'greater': lambda a,b: a > b,
        'lessOrEquals': lambda a,b: a <= b, 'createArray': lambda *v: list(v),
        'contains': lambda a,b: b in a}
    def visit(node):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in functions:
            return functions[node.func.id](*(visit(a) for a in node.args))
        raise AssertionError('Unsupported generated expression')
    return visit(ast.parse(expression, mode='eval').body)


class OperatorInputsTest(unittest.TestCase):
    def setUp(self):
        # Existing synthetic executable schema; never use private tenant evidence.
        guard = {'actions': {'Parse_manifest': {'inputs': {}},
            'Check_unique_identifiers': {'actions': {
                'For_each_paper': {'actions': {'Check_paper_binding': {'actions': {
                    'Get_paper_metadata': {'inputs': {'parameters': {}}},
                    'Check_reviewed_etag': {'actions': {'Append_match': {'inputs': {'value': {}}}},
                        'else': {'actions': {'Append_review_drift': {'inputs': {'value': {}}}}}}
                }}}}, 'Manifest_results': {'inputs': {'paper_readiness': False}}
            }}}, 'else': {'actions': {'Stop_missing_manifest_input': {'inputs': {}}}}}
        self.baseline = {'properties': {'definition': {'triggers': {'manual': {'inputs': {}}},
            'actions': {'Check_manifest_input': guard, 'Initialize_expected_count': {}}},
            'connectionReferences': {'existing': 'preserved'}}}
        self.args = dict(site='https://fictional-example.sharepoint.com/personal/test',
            path='/Documents/Test.docx', name='Test.docx', version='3.0',
            etag='"observed-v3"', paper_ref='P-TEST')

    def test_operator_cannot_supply_path_or_version_token(self):
        out = build_operator_inputs(self.baseline, **self.args)
        d = out['properties']['definition']
        self.assertEqual(set(d['triggers']['manual']['inputs']['schema']['properties']), {'Paper', 'Version'})
        guard = d['actions']['Check_manifest_input']
        self.assertEqual(guard['expression']['and'][1]['equals'][1], 'Compare with observed version 3.0')
        self.assertEqual(guard['runAfter'], {'Selected_manifest': ['Succeeded']})
        binding = guard['actions']['Check_unique_identifiers']['actions']['For_each_paper']['actions']['Check_paper_binding']
        self.assertEqual(binding['expression']['and'][1]['equals'][1], '/Documents/Test.docx')
        self.assertFalse(guard['actions']['Check_unique_identifiers']['actions']['Manifest_results']['inputs']['paper_readiness'])

    def test_preserves_source_and_connection_contract_without_mutating_input(self):
        original = json.dumps(self.baseline, sort_keys=True)
        out = build_operator_inputs(self.baseline, **self.args)
        self.assertEqual(original, json.dumps(self.baseline, sort_keys=True))
        self.assertEqual(out['properties']['connectionReferences'], self.baseline['properties']['connectionReferences'])
        self.assertEqual(out['properties']['definition']['actions']['Selected_manifest']['inputs'][0]['ReviewedETag'], '"observed-v3"')

    def test_refuses_unqualified_binding(self):
        for change in ({'site': 'http://fictional-example.sharepoint.com'}, {'etag': ''}, {'path': 'relative'}):
            with self.assertRaises(ValueError):
                build_operator_inputs(self.baseline, **dict(self.args, **change))

    def preflight_actions(self):
        baseline = build_operator_inputs(self.baseline, **self.args)
        result = build_paper_preflight(baseline, declared_meeting_date='2026-09-28')
        self.assertEqual(result['properties']['connectionReferences'], baseline['properties']['connectionReferences'])
        schema = result['properties']['definition']['triggers']['manual']['inputs']['schema']
        self.assertEqual(set(schema['required']), set(schema['properties']))
        self.assertEqual(schema['properties']['MeetingDate']['default'], 'Not confirmed')
        self.assertEqual(schema['properties']['Pages']['default'], 'Not checked')
        return result['properties']['definition']['actions']['Check_manifest_input']['actions']['Check_unique_identifiers']['actions']

    def exception_codes(self, inputs):
        rows = self.preflight_actions()['Paper_exception_candidates']['inputs']
        return {code for row in rows if (code := evaluate_generated(row['code'], inputs))}

    def test_missing_checks_remain_visible(self):
        self.assertEqual(self.exception_codes({}), {
            'FORMAT_UNKNOWN', 'LENGTH_UNKNOWN', 'READABILITY_UNCONFIRMED',
            'RESTRICTED_CONTENT_UNRESOLVED', 'REVIEW_UNCONFIRMED', 'MEETING_UNCONFIRMED'})

    def test_format_limits_and_wrong_meeting(self):
        confirmed = dict(Readability='Readable', Content='Suitable for existing audience',
            Review='Reviewed this source and version', MeetingConfirmation='Confirmed for selected meeting', MeetingDate='2026-09-28')
        for fmt, limit in [('Brief',1), ('Report',2), ('Slides',3)]:
            self.assertEqual(self.exception_codes(dict(confirmed, PaperFormat=fmt, Pages=str(limit))), set())
            self.assertEqual(self.exception_codes(dict(confirmed, PaperFormat=fmt, Pages=str(limit+1) if limit < 3 else '4 or more')), {'PAGE_LIMIT_EXCEEDED'})
        self.assertEqual(self.exception_codes(dict(confirmed, PaperFormat='Report', Pages='2', MeetingDate='Another meeting')), {'WRONG_MEETING'})
        self.assertIn('FORMAT_UNKNOWN', self.exception_codes(dict(confirmed, PaperFormat='Unknown', Pages='1')))
        self.assertNotIn('WRONG_MEETING', self.exception_codes(dict(confirmed, MeetingDate='Not confirmed')))
        self.assertIn('MEETING_UNCONFIRMED', self.exception_codes(dict(confirmed, MeetingDate='Not confirmed')))

    def test_manual_review_keeps_approval_and_source_claims_separate(self):
        actions = self.preflight_actions()
        result = actions['Paper_preflight']['inputs']
        self.assertFalse(result['paper_readiness'])
        self.assertFalse(result['meeting_source_verified'])
        self.assertEqual(actions['Human_checks']['inputs']['evidence_kind'], 'OPERATOR_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED')
        self.assertIn("empty(body('Metadata_exceptions'))", result['ready_for_manual_review'])
        self.assertEqual(actions['Operator_result']['runAfter'], {'Exception_lines': ['Succeeded']})


if __name__ == '__main__':
    unittest.main()
