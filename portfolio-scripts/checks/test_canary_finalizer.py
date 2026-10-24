"""Exercise the actual workflow finalizer without preview runtimes or network writes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
STEPS = yaml.safe_load((ROOT / '.github/workflows/development-canary.yml').read_text())['jobs']['runtime']['steps']
FINALIZER = next(step for step in STEPS if step.get('name') == 'Record the actual runtime qualification outcome')


class CanaryFinalizer(unittest.TestCase):
    def execute(self, outcome, existing_helper=True, receipt=None):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            helper = root / '.venv-careops-ci/bin/python'
            helper.parent.mkdir(parents=True)
            marker = root / 'unverified-executed'
            ambient = root / 'ambient/bin'
            ambient.mkdir(parents=True)
            fake_python = ambient / 'python'
            fake_python.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\nexit 99\n')
            fake_python.chmod(0o755)
            if existing_helper:
                if outcome == 'success':
                    helper.symlink_to(sys.executable)
                else:
                    helper.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\n')
                    helper.chmod(0o755)
            scripts = root / 'portfolio-scripts'
            scripts.mkdir()
            shutil.copyfile(ROOT / 'portfolio-scripts/ci_delivery.py', scripts / 'ci_delivery.py')
            target = root / '.local/runtime-canary/discovery.json'
            if receipt is not None:
                target.parent.mkdir(parents=True)
                target.write_text(json.dumps(receipt))
            result = subprocess.run(['bash', '-e', '-c', FINALIZER['run']], cwd=root,
                                    env=dict(os.environ, PATH=str(ambient) + os.pathsep + os.environ['PATH'],
                                             GITHUB_WORKSPACE=str(root), HELPER_OUTCOME=outcome,
                                             DISCOVERY_OUTCOME='failure' if receipt is None else 'success',
                                             RUNTIME_TEST_OUTCOME='skipped'), capture_output=True, text=True)
            failure = target.parent / 'helper-failure.json'
            return result, marker.exists(), json.loads((failure if failure.exists() else target).read_text())

    def test_failed_helper_is_never_executed_even_if_present(self):
        result, executed, receipt = self.execute('failure')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(executed)
        self.assertEqual(receipt['state'], 'setup-blocked')
        self.assertFalse(receipt['runtimeTestsExecuted'])

    def test_missing_helper_fails_without_ambient_python(self):
        result, executed, receipt = self.execute('success', existing_helper=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(executed)
        self.assertFalse(receipt['promoted'])

    def test_verified_helper_records_failed_discovery(self):
        result, executed, receipt = self.execute('success')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(executed)
        self.assertEqual(receipt['state'], 'discovery-failed')
        self.assertFalse(receipt['runtimeTestsExecuted'])

    def test_unavailable_preview_remains_unexecuted(self):
        result, _, receipt = self.execute('success', receipt={'state': 'unavailable', 'candidate': None, 'promoted': False, 'manifestRevision': 'a' * 40, 'manifestSha256': 'b' * 64})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(receipt['state'], 'unavailable')
        self.assertFalse(receipt['runtimeTestsExecuted'])


if __name__ == '__main__':
    unittest.main()
