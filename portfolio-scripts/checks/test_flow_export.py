"""Refuse changed definitions/bindings without network access or private fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import warnings
import zipfile

spec = importlib.util.spec_from_file_location('flow_export', Path(__file__).parents[1] / 'verify_flow_export.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MEMBER = 'Workflows/fictional.json'


class FlowExportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.artifact, self.snapshot = self.root / 'solution.zip', self.root / 'snapshot.json'
        self.definition = {'actions': {'Keep_human_edits': {'type': 'Compose', 'inputs': 'preserve'}}, 'triggers': {}}
        self.native = {'properties': {'state': 'Stopped', 'definition': self.definition, 'connectionReferences': {
            'shared_example': {'connectionReferenceLogicalName': 'ex_existing', 'source': 'Invoker',
                               'id': '/providers/Microsoft.PowerApps/apis/shared_example', 'displayName': 'Service metadata'}
        }}}
        self.export = {'schemaVersion': '1.0.0.0', 'properties': {'definition': copy.deepcopy(self.definition),
            'templateName': None, 'connectionReferences': {'shared_example': {
                'runtimeSource': 'invoker', 'connection': {'connectionReferenceLogicalName': 'ex_existing'},
                'api': {'name': 'shared_example'}}}}}

    def run_verifier(self, extra=None):
        self.snapshot.write_text(json.dumps(self.native))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.artifact, 'w') as z:
                z.writestr(MEMBER, json.dumps(self.export))
                if extra:
                    z.writestr(*extra)
        return module.verify(self.artifact, MEMBER, self.snapshot)

    def test_exact_graph_explicit_reference_mapping_and_no_deployment_claim(self):
        result = self.run_verifier()
        self.assertTrue(result['qualified'])
        self.assertEqual(result['connectionReferenceCount'], 1)
        self.assertFalse(result['runtimeOrImportQualified'])
        self.assertFalse(result['nativeSnapshotAuthenticityVerified'])
        self.assertFalse(result['wholeSolutionCoverageVerified'])
        self.assertEqual(len(result['artifactSha256']), 64)

    def test_changed_or_removed_action_is_not_normalized(self):
        for definition in [{'actions': {}}, {'actions': {'Keep_human_edits': {'type': 'Compose', 'inputs': 'overwrite'}}, 'triggers': {}}]:
            with self.subTest(definition=definition):
                self.export['properties']['definition'] = definition
                with self.assertRaisesRegex(ValueError, 'definition differs'):
                    self.run_verifier()

    def test_connection_rebinding_and_invocation_change_are_refused(self):
        for field, value in [('connection', {'connectionReferenceLogicalName': 'ex_rebound'}),
                             ('api', {'name': 'shared_other'}), ('runtimeSource', 'embedded')]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.export)
                self.export['properties']['connectionReferences']['shared_example'][field] = value
                with self.assertRaisesRegex(ValueError, 'identity, API or invocation'):
                    self.run_verifier()
                self.export = original

    def test_missing_and_extra_reference_coverage_are_refused(self):
        self.export['properties']['connectionReferences'] = {}
        with self.assertRaisesRegex(ValueError, 'coverage differs'):
            self.run_verifier()

    def test_uncompared_properties_and_nonnull_template_are_refused(self):
        self.export['properties']['unexpected'] = True
        with self.assertRaisesRegex(ValueError, 'Uncompared'):
            self.run_verifier()
        del self.export['properties']['unexpected']
        self.export['properties']['templateName'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'non-null'):
            self.run_verifier()

    def test_unknown_reference_shape_and_schema_are_refused(self):
        self.export['properties']['connectionReferences']['shared_example']['connection']['connectionName'] = 'hidden-binding'
        with self.assertRaisesRegex(ValueError, 'Unsupported package reference'):
            self.run_verifier()
        self.export['schemaVersion'] = 'future'
        with self.assertRaisesRegex(ValueError, 'envelope'):
            self.run_verifier()

    def test_json_ambiguity_and_numeric_type_changes_are_refused(self):
        for raw in [b'{"x":1,"x":2}', b'{"x":NaN}']:
            with self.assertRaises(ValueError):
                module.strict_json(raw)
        self.native['properties']['definition']['integer'] = 1
        self.export['properties']['definition']['integer'] = True
        with self.assertRaisesRegex(ValueError, 'definition differs'):
            self.run_verifier()

    def test_archive_ambiguity_and_traversal_are_refused(self):
        for name in [MEMBER, MEMBER.upper(), '../outside.json', 'Workflows/../outside.json']:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'archive identity'):
                self.run_verifier((name, '{}'))

    def test_cli_preserves_existing_receipt(self):
        self.run_verifier()
        output = self.root / 'receipt.json'
        output.write_text('existing human evidence')
        result = subprocess.run([sys.executable, str(Path(module.__file__)),
                                 '--artifact', str(self.artifact), '--workflow-member', MEMBER,
                                 '--snapshot', str(self.snapshot), '--output', str(output)],
                                capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(), 'existing human evidence')

    def test_equal_instant_timestamp_literals_still_differ(self):
        self.native['properties']['definition']['actions']['Keep_human_edits']['inputs'] = {
            'attempts': [{'observed': '2026-10-22T01:02:03.350Z'}]}
        self.export['properties']['definition']['actions']['Keep_human_edits']['inputs'] = {
            'attempts': [{'observed': '2026-10-22T01:02:03.35Z'}]}
        with self.assertRaisesRegex(ValueError, 'definition differs'):
            self.run_verifier()

    def test_profile_specific_minimum_is_opt_in(self):
        wait = {'type': 'Wait', 'inputs': {'interval': {'count': 1, 'unit': 'Second'}}}
        self.definition['actions']['Delay'] = wait
        self.export['properties']['definition'] = copy.deepcopy(self.definition)
        self.assertIsNone(self.run_verifier()['postponeIntervalCheck'])
        self.assertEqual(module.verify(self.artifact, MEMBER, self.snapshot, 1)
                         ['postponeIntervalCheck']['relativeWaitCount'], 1)
        with self.assertRaisesRegex(ValueError, 'below the selected'):
            module.verify(self.artifact, MEMBER, self.snapshot, 5)
        wait['inputs']['interval']['count'] = 5
        self.export['properties']['definition'] = copy.deepcopy(self.definition)
        self.run_verifier()
        self.assertEqual(module.verify(self.artifact, MEMBER, self.snapshot, 5)
                         ['postponeIntervalCheck']['minimumSeconds'], 5)

    def test_cli_timing_refusal_writes_no_receipt(self):
        self.definition['actions']['Delay'] = {'type': 'Wait',
            'inputs': {'interval': {'count': 1, 'unit': 'Second'}}}
        self.export['properties']['definition'] = copy.deepcopy(self.definition)
        self.run_verifier()
        output = self.root / 'timing.json'
        command = [sys.executable, str(Path(module.__file__)), '--artifact', str(self.artifact),
                   '--workflow-member', MEMBER, '--snapshot', str(self.snapshot),
                   '--output', str(output), '--minimum-postpone-seconds']
        refused = subprocess.run(command + ['5'], capture_output=True)
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(output.exists())
        accepted = subprocess.run(command + ['1'], capture_output=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(json.loads(output.read_text())['postponeIntervalCheck']['relativeWaitCount'], 1)

    def test_nested_containers_and_data_are_distinguished(self):
        wait = {'type': 'Wait', 'inputs': {'interval': {'count': 5, 'unit': 'Second'}}}
        actions = {'Loop': {'type': 'Foreach', 'actions': {
            'Condition': {'type': 'If', 'actions': {'Yes': wait},
                          'else': {'actions': {'Choice': {'type': 'Switch',
                              'cases': {'A': {'actions': {'Delay': wait}}},
                              'default': {'actions': {'Scope': {'type': 'Scope', 'actions': {
                                  'Until': {'type': 'Until', 'actions': {'Delay': wait}}}}}}}}}}}},
            'Data': {'type': 'Compose', 'inputs': {'type': 'Wait', 'inputs': {'interval': {'count': 0}}}},
            'Absolute': {'type': 'Wait', 'inputs': {'until': '@variables("deadline")'}}}
        result = module.check_postpone_intervals({'actions': actions,
            'triggers': {'Schedule': {'type': 'Recurrence', 'recurrence': {'frequency': 'Second', 'interval': 1}}}}, 5)
        self.assertEqual(result['relativeWaitCount'], 3)
        self.assertEqual(result['absoluteWaitCountExcluded'], 1)
        self.assertFalse(result['performanceProfileVerified'])

    def test_dynamic_invalid_and_unknown_intervals_are_not_qualified(self):
        for count, unit in [('@variables("delay")', 'Second'), (True, 'Second'),
                            (0, 'Second'), (-1, 'Second'), (1.0, 'Second'), (5, 'Unknown')]:
            with self.subTest(count=count, unit=unit), self.assertRaises(ValueError):
                module.check_postpone_intervals({'actions': {'Delay': {'type': 'Wait',
                    'inputs': {'interval': {'count': count, 'unit': unit}}}}}, 5)
        for unit in ('Minute', 'Hour', 'Day', 'Week', 'Month'):
            result = module.check_postpone_intervals({'actions': {'Delay': {'type': 'Wait',
                'inputs': {'interval': {'count': 1, 'unit': unit}}}}}, 5)
            self.assertEqual(result['relativeWaitCount'], 1)
        for minimum in (True, 0, 2, 5.0):
            with self.assertRaises(ValueError):
                module.check_postpone_intervals({'actions': {}}, minimum)

    def test_input_symlink_is_refused(self):
        self.run_verifier()
        alias = self.root / 'alias.zip'
        alias.symlink_to(self.artifact)
        with self.assertRaisesRegex(ValueError, 'regular input'):
            module.verify(alias, MEMBER, self.snapshot)


if __name__ == '__main__':
    unittest.main()
