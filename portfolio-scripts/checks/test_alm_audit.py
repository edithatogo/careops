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
