"""Exercise the check with a local fake CLI; no authentication/network code runs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).parents[2] / 'powerplatform/scripts/pac-environment-check.ps1'


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell required')
class EnvironmentCheckTests(unittest.TestCase):
    def invoke(self, url, code='0', output='Fixture organization identity'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mock = root / 'pac.ps1'
            calls = root / 'calls.json'
            mock.write_text("$args | ConvertTo-Json -Compress | Set-Content -LiteralPath $env:TEST_CALLS\nWrite-Output $env:TEST_OUTPUT\n$global:LASTEXITCODE = [int]$env:TEST_EXIT\n")
            env = dict(os.environ, TEST_CALLS=str(calls), TEST_OUTPUT=output, TEST_EXIT=code)
            result = subprocess.run(['pwsh', '-NoProfile', '-File', str(SCRIPT), '-PacPath', str(mock), '-EnvironmentUrl', url], env=env, text=True, capture_output=True)
            return result, json.loads(calls.read_text()) if calls.exists() else None

    def test_exact_target_only_and_no_auth_mutation(self):
        result, calls = self.invoke('https://fixture.crm6.dynamics.com')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(calls, ['org', 'who', '--environment', 'https://fixture.crm6.dynamics.com/'])
        self.assertIn('Inspect the returned identity', result.stdout)

    def test_failed_native_read_never_reports_success(self):
        result, calls = self.invoke('https://fixture.crm6.dynamics.com/', code='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('read succeeded', result.stdout)
        self.assertEqual(calls[:2], ['org', 'who'])

    def test_empty_evidence_is_failure(self):
        result, _ = self.invoke('https://fixture.crm6.dynamics.com/', output='')
        self.assertNotEqual(result.returncode, 0)

    def test_missing_or_unsafe_target_never_invokes_cli(self):
        for url in ['', 'http://fixture.crm6.dynamics.com/', 'https://user@fixture.crm6.dynamics.com/', 'https://fixture.crm6.dynamics.com/path', 'https://fixture.crm6.dynamics.com/?q=1']:
            with self.subTest(url=url):
                result, calls = self.invoke(url)
                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(calls)


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell required')
class DeploymentTargetTests(unittest.TestCase):
    def invoke(self, url, who_code='0'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mock, calls, package = root / 'pac.ps1', root / 'calls.jsonl', root / 'fixture.zip'
            package.write_bytes(b'local fake package; never submitted')
            mock.write_text("ConvertTo-Json -InputObject @($args) -Compress | Add-Content -LiteralPath $env:TEST_CALLS\nWrite-Output 'Fixture native result'\n$global:LASTEXITCODE = if ($args[0] -eq 'org') { [int]$env:TEST_EXIT } else { 0 }\n")
            env = dict(os.environ, TEST_CALLS=str(calls), TEST_EXIT=who_code)
            script = SCRIPT.with_name('pac-solution-deploy.ps1')
            result = subprocess.run(['pwsh', '-NoProfile', '-File', str(script), '-PacPath', str(mock), '-SolutionPath', str(package), '-EnvironmentUrl', url], env=env, text=True, capture_output=True)
            return result, [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []

    def test_existing_session_preserved_and_both_commands_targeted(self):
        result, calls = self.invoke('https://fixture.crm6.dynamics.com/')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], ['org', 'who', '--environment', 'https://fixture.crm6.dynamics.com/'])
        self.assertEqual(calls[1][:2], ['solution', 'import'])
        self.assertEqual(calls[1][-2:], ['--environment', 'https://fixture.crm6.dynamics.com/'])

    def test_failed_read_prevents_import(self):
        result, calls = self.invoke('https://fixture.crm6.dynamics.com/', who_code='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][:2], ['org', 'who'])

    def test_missing_target_prevents_all_cli_calls(self):
        result, calls = self.invoke('')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])
