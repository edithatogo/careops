"""Exercise the actual reusable job identity guard before any code checkout."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class PolicyIdentity(unittest.TestCase):
    def test_called_workflow_commit_must_match_the_tooling_commit(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/reusable-source-security.yml').read_text())
        script = next(step for step in workflow['jobs']['baseline']['steps'] if step.get('id') == 'policy')['run']
        commit = 'c' * 40
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'job-output'
            env = os.environ.copy()
            env.update(POLICY_REVISION=commit, GITHUB_OUTPUT=str(output))
            for identity, success in [({'workflow_sha': commit, 'workflow_repository': 'edithatogo/careops'}, True), ({'workflow_sha': 'd' * 40, 'workflow_repository': 'edithatogo/careops'}, False), ({'workflow_sha': commit, 'workflow_repository': 'other/repository'}, False), ({}, False), ({'workflow_sha': 'main', 'workflow_repository': 'edithatogo/careops'}, False)]:
                env['WORKFLOW_IDENTITY'] = json.dumps(identity)
                with self.subTest(identity=identity):
                    run = subprocess.run(['bash', '-euc', script], env=env, capture_output=True, text=True)
                    self.assertEqual(run.returncode == 0, success, run.stderr)
            self.assertEqual(output.read_text(), 'revision=' + commit + '\n')


class CommittedLock(unittest.TestCase):
    def test_actual_workflow_gate_rejects_an_uncommitted_generated_lock(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/lock-refresh.yml').read_text())
        steps = workflow['jobs']['lock']['steps']
        gate = next(s for s in steps if s.get('name') == 'Require qualified generated files in the source commit')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', tmp], check=True)
            lock = root / 'requirements-ci.lock'
            lock.write_text('qualified exact versions and hashes\n')
            subprocess.run(['git', '-C', tmp, 'add', 'requirements-ci.lock'], check=True)
            subprocess.run(['git', '-C', tmp, '-c', 'user.name=CI', '-c', 'user.email=ci@example.invalid', 'commit', '-qm', 'baseline'], check=True)
            clean = subprocess.run(['bash', '-euc', gate['run']], cwd=tmp, capture_output=True)
            self.assertEqual(clean.returncode, 0)
            lock.write_text('new generated exact versions and hashes\n')
            stale = subprocess.run(['bash', '-euc', gate['run']], cwd=tmp, capture_output=True)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn(b'new generated', stale.stdout)
        # Failed regeneration must still retain its repair candidate.
        self.assertIn('!cancelled()', steps[-1]['if'])


class SecurityGate(unittest.TestCase):
    def test_consolidated_required_gate_refuses_failed_skipped_or_cancelled_children(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/security.yml').read_text())
        gate = workflow['jobs']['gate']
        self.assertEqual(set(gate['needs']), {'security', 'fuzz', 'codeql'})
        script = gate['steps'][0]['run']
        for results, success in [('success,success,success', True), ('success,failure,success', False), ('skipped,success,success', False), ('success,success,cancelled', False)]:
            with self.subTest(results=results):
                result = subprocess.run(['bash', '-euc', script], env={**os.environ, 'RESULTS': results}, capture_output=True)
                self.assertEqual(result.returncode == 0, success)


class SharedCallerLock(unittest.TestCase):
    def test_actual_shared_step_accepts_absence_but_rejects_a_stale_caller_lock(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/reusable-source-security.yml').read_text())
        step = next(s for s in workflow['jobs']['baseline']['steps'] if s.get('name') == 'Reject stale exact caller CI tool declarations')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            helper = root / '.careops-ci-tools/portfolio-scripts/ci_delivery.py'
            helper.parent.mkdir(parents=True)
            helper.write_bytes((ROOT / 'portfolio-scripts/ci_delivery.py').read_bytes())
            def run():
                return subprocess.run(['bash', '-euc', step['run']], cwd=tmp, capture_output=True, env={**os.environ, 'PATH': str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')})
            self.assertEqual(run().returncode, 0)
            (root / 'requirements-ci.txt').write_text('ruff==0.17.1\n')
            (root / 'requirements-ci.lock').write_text('ruff==0.17.1\n')
            self.assertEqual(run().returncode, 0)
            (root / 'requirements-ci.lock').write_text('ruff==0.17.0\n')
            self.assertNotEqual(run().returncode, 0)


if __name__ == '__main__':
    unittest.main()
