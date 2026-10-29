"""Exercise committed-source isolation and actual component inventory semantics."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('alm_audit', Path(__file__).parents[1] / 'audit_power_platform.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AlmAuditTests(unittest.TestCase):
    def test_component_identity_includes_type_and_repeated_keys_are_visible(self):
        result = audit.inspect_solution(b'<ImportExportXml><SolutionManifest><UniqueName>Example</UniqueName><Version>1.2.3.4</Version><RootComponents><RootComponent type="29" id="x"/><RootComponent type="29" id="x"/><RootComponent type="1" id="x"/></RootComponents></SolutionManifest></ImportExportXml>')
        self.assertEqual(result['rootComponentCount'], 3)
        self.assertEqual(result['duplicateRootKeys'], 1)
        self.assertEqual(result['version'], '1.2.3.4')

    def test_guid_spelling_cannot_hide_duplicate_component_membership(self):
        result = audit.inspect_solution(b'''<ImportExportXml><SolutionManifest>
          <RootComponents>
            <RootComponent type="29" id="{00000000-0000-4000-8000-000000000ABC}"/>
            <RootComponent type="29" id="00000000-0000-4000-8000-000000000abc"/>
            <RootComponent type="1" id="00000000-0000-4000-8000-000000000abc"/>
            <RootComponent type="29" id="00000000-0000-4000-8000-000000000def"/>
          </RootComponents></SolutionManifest></ImportExportXml>''')
        self.assertEqual(result['duplicateRootKeys'], 1)
        self.assertEqual(result['rootComponentCount'], 4)

    def test_solution_version_and_publisher_are_not_confused(self):
        raw = b'''<ImportExportXml><SolutionManifest><UniqueName>Example</UniqueName>
          <Version>0.1.0.0</Version><Publisher><UniqueName>ExamplePublisher</UniqueName>
          <Version>9.9.9.9</Version><CustomizationPrefix>exmp</CustomizationPrefix>
          </Publisher></SolutionManifest></ImportExportXml>'''
        result = audit.inspect_solution(raw)
        self.assertEqual(result['uniqueName'], 'Example')
        self.assertEqual(result['publisherUniqueName'], 'ExamplePublisher')
        self.assertEqual(result['publisherPrefix'], 'exmp')
        self.assertTrue(result['versionFormatValid'])
        self.assertFalse(audit.inspect_solution(raw.replace(b'0.1.0.0', b'0.1'))['versionFormatValid'])
        self.assertFalse(audit.inspect_solution(b'<ImportExportXml/>')['versionFormatValid'])

    def test_dirty_and_untracked_files_do_not_become_committed_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def run(*args):
                subprocess.run(['git', '-C', directory, *args], check=True, capture_output=True)
            run('init')
            (root / 'README.md').write_text('source')
            run('add', '.')
            run('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'source')
            (root / 'Other').mkdir()
            (root / 'Other/Solution.xml').write_text('<invalid')
            (root / 'README.md').write_text('human edit')
            result = audit.audit(root)
            self.assertEqual(result['trackedFiles'], 1)
            self.assertEqual(result['solutions'], [])
            self.assertEqual(result['nativeCoverage'], 'not-verified')
            self.assertEqual((root / 'README.md').read_text(), 'human edit')

    def test_replacement_refs_cannot_substitute_advertised_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def run(*args):
                return subprocess.check_output(['git', '-C', directory, *args], stderr=subprocess.DEVNULL)
            run('init')
            (root / 'first.txt').write_text('original')
            run('add', '.')
            run('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'first')
            first = run('rev-parse', 'HEAD').decode().strip()
            (root / 'second.txt').write_text('replacement-only')
            run('add', '.')
            run('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'second')
            second = run('rev-parse', 'HEAD').decode().strip()
            run('replace', first, second)
            result = audit.audit(root, first)
            self.assertEqual(result['sourceCommit'], first)
            self.assertEqual(result['trackedFiles'], 1)


    def test_github_workflow_count_cannot_be_read_as_cloud_flow_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ['.github/workflows/source.yml', '.github/workflows/security.yaml', 'Workflows/selected.json', 'docs/workflow.yml']:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}')
            subprocess.run(['git', '-C', directory, 'init'], check=True, capture_output=True)
            subprocess.run(['git', '-C', directory, 'add', '.'], check=True, capture_output=True)
            subprocess.run(['git', '-C', directory, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'source'], check=True, capture_output=True)
            result = audit.audit(root)
            self.assertEqual(result['githubWorkflowFiles'], 2)
            self.assertNotIn('workflowFiles', result)
            self.assertEqual(result['schemaVersion'], 2)
            self.assertEqual(result['nativeCoverage'], 'not-verified')

    def test_authoring_profile_presence_is_not_runtime_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for name in ['scripts/powerplatform_validation.py', 'scripts/schemas/power-automate-profile.json']:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fictional', '-c', 'user.email=fictional@example.invalid', 'commit', '-qm', 'Fixture'], check=True)
            result = audit.audit(root)['authoringAssurance']
            self.assertEqual(result['outcome'], 'unverified')
            self.assertFalse(result['nativeAcceptance'])
            self.assertEqual(len(result['validatorSources']), 1)
            self.assertEqual(len(result['profileSources']), 1)
