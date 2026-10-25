"""Exercise the actual reusable job identity guard before any code checkout."""
import json
import os
import shlex
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
        script = next(step for step in workflow['jobs']['baseline']['steps'] if step.get('id') == 'policy')['run'].replace('python3', shlex.quote(sys.executable), 1)
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
    def test_parent_jobs_isolate_helpers_after_each_selected_runtime(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            if path.name == 'reusable-source-security.yml':
                continue
            workflow = yaml.safe_load(path.read_text())
            for job in workflow.get('jobs', {}).values():
                steps = job.get('steps', [])
                for index, step in enumerate(steps):
                    if not step.get('uses', '').startswith('actions/setup-python@'):
                        continue
                    with self.subTest(workflow=path.name, runtime=step.get('id')):
                        environment = steps[index + 1]
                        self.assertEqual(environment.get('name'), 'Select verified repository-local Python')
                        self.assertEqual(environment['env']['SELECTED_PYTHON'], '${{ steps.' + step['id'] + '.outputs.python-path }}')
                        self.assertEqual(environment['env']['EXPECTED_PYTHON'], step['with']['python-version'])
                        self.assertEqual(environment.get('if'), step.get('if'))
                        self.assertTrue(any(s.get('uses', '').startswith('actions/checkout@') for s in steps[:index]))

    def test_shared_bootstrap_refuses_caller_contents_and_symlink_targets(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/reusable-source-security.yml').read_text())
        bootstrap = next(s for s in workflow['jobs']['baseline']['steps'] if s.get('name') == 'Select and verify repository-local helper environment')
        for symlink in (False, True):
            with self.subTest(symlink=symlink), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                target = root / '.venv-careops-ci'
                if symlink:
                    target.symlink_to(root / 'missing-destination', target_is_directory=True)
                else:
                    payload = target / 'lib/python3.15/site-packages/sitecustomize.py'
                    payload.parent.mkdir(parents=True)
                    payload.write_text("raise RuntimeError('Caller payload must not run')\n")
                result = subprocess.run(['bash', '-euc', bootstrap['run']], env={**os.environ, 'GITHUB_WORKSPACE': tmp, 'SELECTED_PYTHON': sys.executable, 'GITHUB_PATH': str(root / 'github-path')}, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b'Refusing a pre-existing helper environment', result.stderr)
                self.assertFalse((root / 'github-path').exists())
                self.assertTrue(target.is_symlink() if symlink else payload.exists())

    def test_helper_environment_survives_checkout_and_selects_the_actual_interpreter(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/reusable-source-security.yml').read_text())
        steps = workflow['jobs']['baseline']['steps']
        bootstrap = next(s for s in steps if s.get('name') == 'Select and verify repository-local helper environment')
        checkout = next(s for s in steps if s.get('uses', '').startswith('actions/checkout@'))
        helper = next(s for s in steps if s.get('name') == 'Reject stale exact caller CI tool declarations')
        self.assertLess(steps.index(checkout), steps.index(bootstrap))
        self.assertLess(steps.index(bootstrap), steps.index(helper))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path_file = root / 'github-path'
            (root / 'venv.py').write_text("raise RuntimeError('Caller module must not run')\n")
            (root / 'sitecustomize.py').write_text("raise RuntimeError('Caller site hook must not run')\n")
            result = subprocess.run(['bash', '-euc', bootstrap['run']], cwd=tmp, env={**os.environ, 'GITHUB_WORKSPACE': tmp, 'SELECTED_PYTHON': sys.executable, 'GITHUB_PATH': str(path_file)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            selected = path_file.read_text().strip()
            probe = subprocess.run(['python', '-c', 'import json,sys; print(json.dumps([list(sys.version_info[:3]),sys.prefix,sys.base_prefix]))'], env={**os.environ, 'PATH': selected + os.pathsep + os.environ.get('PATH', '')}, capture_output=True, text=True, check=True)
            version, prefix, base = json.loads(probe.stdout)
            self.assertEqual(version, [3, 15, 1])
            self.assertEqual(Path(prefix).resolve(), (root / '.venv-careops-ci').resolve())
            self.assertNotEqual(prefix, base)

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
