"""Regression tests for CI outcomes and immutable dependency resolution."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('ci_delivery', Path(__file__).resolve().parents[1] / 'ci_delivery.py')
CI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CI)


class DeliveryTests(unittest.TestCase):
    def test_required_ci_refuses_stale_or_missing_declared_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'requirements-ci.txt').write_text('pip_audit==2.10.1\n')
            lock = root / 'requirements-ci.lock'
            lock.write_text('pip-audit==2.10.1 \\\n    --hash=sha256:example\n')
            CI.verify_declared_lock(root)
            for stale in ['pip-audit==2.9.0\n', 'ruff==0.17.1\n']:
                lock.write_text(stale)
                with self.assertRaises(ValueError):
                    CI.verify_declared_lock(root)

    def test_annotated_tag_is_peeled_before_commit_comparison(self):
        tag, commit = 'a' * 40, 'b' * 40
        self.assertEqual(CI.peel_commit({'type': 'tag', 'sha': tag}, lambda _: {'object': {'type': 'commit', 'sha': commit}}), commit)
        self.assertEqual(CI.peel_commit({'type': 'commit', 'sha': commit}, lambda _: self.fail('Unexpected tag fetch')), commit)
        for obj in [{'type': 'tree', 'sha': commit}, {'type': 'commit', 'sha': 'main'}]:
            with self.assertRaises(ValueError):
                CI.peel_commit(obj, lambda _: {})
        with self.assertRaises(ValueError):
            CI.peel_commit({'type': 'tag', 'sha': tag}, lambda _: {'object': {'type': 'tag', 'sha': tag}})

    def test_billing_refusal_is_not_test_failure_or_pass(self):
        run = {'status': 'completed', 'conclusion': 'failure'}
        annotation = [{'message': 'The job was not started because recent account payments have failed or your spending limit needs to be increased.'}]
        self.assertEqual(CI.classify_run(run, [{'conclusion': 'failure', 'steps': []}], annotation)['state'], 'billing-blocked')
        self.assertEqual(CI.classify_run(run, [], [])['state'], 'unverified-failure')
        executed = [{'name': 'tests', 'conclusion': 'failure', 'steps': [{'status': 'completed', 'conclusion': 'failure'}]}]
        mixed = CI.classify_run(run, executed, annotation)
        self.assertEqual(mixed['state'], 'executed-failure')
        self.assertTrue(mixed['billingAnnotationPresent'])
        self.assertEqual(mixed['executedFailureJobs'], ['tests'])

    def test_pending_skipped_cancelled_and_green_remain_distinct(self):
        for conclusion in ['skipped', 'cancelled', 'timed_out']:
            self.assertEqual(CI.classify_run({'status': 'completed', 'conclusion': conclusion}, [], [])['state'], conclusion)
        self.assertEqual(CI.classify_run({'status': 'queued'}, [], [])['state'], 'pending')
        self.assertEqual(CI.classify_run({'status': 'completed', 'conclusion': 'success'}, [], [])['state'], 'unverified')
        self.assertEqual(CI.classify_run({'status': 'completed', 'conclusion': 'success'}, [{'conclusion': 'success'}], [])['state'], 'passed')

    def test_only_exact_unique_registry_requirements_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'requirements.txt'
            path.write_text('# Qualified tools\nruff==0.17.1\npip-audit==2.10.1\n')
            self.assertEqual(CI.exact_requirements(path)['ruff'], '0.17.1')
            for content in ['', 'ruff>=0.17', 'ruff @ https://example.invalid/package', 'ruff==0.17.1\nRUFF==0.17.1']:
                path.write_text(content)
                with self.subTest(content=content), self.assertRaises(ValueError):
                    CI.exact_requirements(path)

    def test_lock_output_stays_local_and_generated_header_uses_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / 'requirements-ci.txt').write_text('ruff==0.17.1\n')
            output = root / 'requirements-ci.lock'
            def compile_lock(command, **kwargs):
                self.assertEqual(kwargs['cwd'], root)
                self.assertEqual(command[3], 'requirements-ci.txt')
                self.assertNotIn(str(root), ' '.join(command))
                output.write_text('ruff==0.17.1 \\\n    --hash=sha256:' + 'a' * 64 + '\n')
            with patch.object(CI.subprocess, 'run', side_effect=compile_lock):
                result = CI.regenerate(root, output)
                self.assertEqual(result['dependencies'], {'ruff': '0.17.1'})
                self.assertFalse(result['promoted'])
            with self.assertRaises(ValueError):
                CI.regenerate(root, root.parent / 'outside.lock')

    def test_classifier_cli_keeps_account_context_out_of_logs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'input.json'
            source.write_text(json.dumps({'run': {'status': 'completed', 'conclusion': 'failure'}, 'jobs': [], 'annotations': [{'message': 'recent account payments have failed'}]}))
            output = root / '.local/outcome.json'
            cli = [sys.executable, str(Path(CI.__file__).resolve()), 'classify', '--input', str(source), '--output', str(output)]
            result = subprocess.run(cli, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())['state'], 'billing-blocked')
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertNotIn('billing', result.stdout)
            self.assertNotIn('payments', result.stdout)
            cli[-1] = str(root / 'public-outcome.json')
            self.assertNotEqual(subprocess.run(cli, cwd=root, capture_output=True).returncode, 0)

    def test_preview_discovery_does_not_downgrade_or_invent_a_runtime(self):
        def release(version, platform='24.04', arch='x64'):
            return {'version': version, 'stable': False, 'files': [{'platform': 'linux', 'platform_version': platform, 'arch': arch, 'download_url': 'https://github.com/actions/python-versions/releases/download/fixture/python.tar.gz'}]}
        self.assertEqual(CI.select_python_preview([release('3.15.0-rc.3')])['state'], 'unavailable')
        manifest = [release('3.16.0-alpha.1'), release('3.16.0-alpha.2'), release('3.17.0-alpha.1', arch='arm64'), release('3.18.0-alpha.1', platform='22.04')]
        result = CI.select_python_preview(manifest)
        self.assertEqual(result['candidate'], '3.16.0-alpha.2')
        self.assertFalse(result['runtimeTestsExecuted'])
        self.assertFalse(result['promoted'])
        self.assertEqual(CI.select_python_preview([])['state'], 'unavailable')

    def test_runtime_receipt_records_executed_failed_and_unavailable_outcomes(self):
        candidate = {'candidate': '3.16.0-alpha.2', 'runtimeTestsExecuted': False, 'promoted': False}
        for outcome, state, executed in [('success', 'qualified', True), ('failure', 'executed-failure', True), ('skipped', 'setup-blocked', False), ('cancelled', 'cancelled', False)]:
            with self.subTest(outcome=outcome):
                receipt = CI.finalize_runtime(candidate, outcome)
                self.assertEqual(receipt['state'], state)
                self.assertEqual(receipt['runtimeTestsExecuted'], executed)
                self.assertFalse(receipt['promoted'])
        absent = CI.select_python_preview([])
        self.assertEqual(CI.finalize_runtime(absent, 'skipped')['state'], 'unavailable')
        with self.assertRaises(ValueError):
            CI.finalize_runtime(absent, 'success')
        with self.assertRaises(ValueError):
            CI.finalize_runtime(candidate, 'unknown')

    def test_unsuccessful_discovery_is_never_unavailable_or_qualified(self):
        partial = {'candidate': '3.16.0-alpha.2', 'manifestSha256': 'a' * 64}
        for outcome, state in [('failure', 'discovery-failed'), ('cancelled', 'cancelled'), ('skipped', 'not-executed')]:
            receipt = CI.finalize_runtime(partial, 'skipped', outcome)
            self.assertEqual(receipt['state'], state)
            self.assertEqual(receipt['discoveryOutcome'], outcome)
            self.assertEqual(receipt['manifestSha256'], partial['manifestSha256'])
            self.assertFalse(receipt['runtimeTestsExecuted'])
            self.assertFalse(receipt['promoted'])
        for runtime_outcome in ['success', 'failure']:
            with self.assertRaises(ValueError):
                CI.finalize_runtime(partial, runtime_outcome, 'failure')

    def test_actual_cli_finalizes_missing_partial_and_corrupt_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / 'nested/discovery.json'
            def run(discovery_outcome):
                return subprocess.run([sys.executable, str(Path(CI.__file__)), 'runtime-finalize', '--receipt', str(receipt),
                                       '--outcome', 'skipped', '--discovery-outcome', discovery_outcome], capture_output=True)
            result = run('failure')
            self.assertEqual(result.returncode, 0, result.stderr)
            value = json.loads(receipt.read_text())
            self.assertEqual(value['state'], 'discovery-failed')
            self.assertFalse(value['promoted'])
            receipt.write_text(json.dumps({'candidate': None, 'manifestRevision': 'a' * 40}))
            self.assertEqual(run('failure').returncode, 0)
            self.assertEqual(json.loads(receipt.read_text())['manifestRevision'], 'a' * 40)
            bad = b'{incomplete discovery'
            receipt.write_bytes(bad)
            self.assertEqual(run('failure').returncode, 1)
            self.assertEqual(json.loads(receipt.read_text())['state'], 'evidence-invalid')
            self.assertEqual(receipt.with_name(receipt.name + '.invalid').read_bytes(), bad)
            receipt.unlink()
            self.assertEqual(run('success').returncode, 1)
            self.assertEqual(json.loads(receipt.read_text())['state'], 'evidence-invalid')


if __name__ == '__main__':
    unittest.main()
