"""Source provenance and unavailable-module refusal for the real integration gate."""
import importlib.util
import json
import os
import yaml
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/qualify_public_module_runtime.py'
spec = importlib.util.spec_from_file_location('public_runtime', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Provenance(unittest.TestCase):
    def test_exact_revision_and_dirty_tracked_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            git('init')
            (root / 'source.txt').write_text('qualified source\n')
            git('add', 'source.txt')
            git('-c', 'user.name=Synthetic CI', '-c', 'user.email=synthetic@example.invalid', 'commit', '-m', 'fixture')
            commit = git('rev-parse', 'HEAD')
            module.verify_source(root, commit)
            with self.assertRaises(ValueError):
                module.verify_source(root, '0' * 40)
            (root / 'source.txt').write_text('changed source\n')
            with self.assertRaises(subprocess.CalledProcessError):
                module.verify_source(root, commit)

    def test_actual_terminal_receipt_handles_bootstrap_failure_and_preserves_scope(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/credentialing-cross-module.yml').read_text())
        step = next(step for step in workflow['jobs']['public-runtime']['steps'] if step.get('name') == 'Record terminal execution outcomes')
        for install, qualification, existing in [('failure', 'skipped', False), ('success', 'success', True)]:
            with self.subTest(install=install), tempfile.TemporaryDirectory() as temporary:
                receipt = Path(temporary) / 'dist/public-runtime-compatibility.json'
                if existing:
                    receipt.parent.mkdir()
                    receipt.write_text(json.dumps({'passed': True, 'testsRun': 9, 'producerRuntimeQualified': False}))
                env = {**os.environ, 'GITHUB_SHA': '1' * 40, 'INSTALL_OUTCOME': install, 'QUALIFICATION_OUTCOME': qualification}
                subprocess.run(['bash', '-e', '-c', step['run']], cwd=temporary, env=env, check=True)
                data = json.loads(receipt.read_text())
                self.assertIs(data['passed'], existing)
                self.assertIs(data['producerRuntimeQualified'], False)
                self.assertEqual(data['installOutcome'], install)
                self.assertEqual(data['qualificationOutcome'], qualification)

    def test_absent_modules_fail_with_retained_unqualified_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / 'receipt.json'
            result = subprocess.run([sys.executable, str(SCRIPT), '--module-root', str(root), '--receipt', str(receipt)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            data = json.loads(receipt.read_text())
            self.assertIs(data['passed'], False)
            self.assertIs(data['producerRuntimeQualified'], False)
            self.assertIs(data['productionWrites'], False)
            self.assertEqual(data['setupFailure'], 'FileNotFoundError')


if __name__ == '__main__':
    unittest.main()
