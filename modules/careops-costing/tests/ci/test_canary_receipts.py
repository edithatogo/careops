"""Execute actual canary receipts on setup, dependency, audit and build failures."""
import json
from itertools import product
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class CanaryReceipt(unittest.TestCase):
    def test_actual_receipt_classifies_every_executed_stage(self):
        workflow = (ROOT / '.github/workflows/development-canary.yml').read_text()
        step = workflow.split('      - name: Record exact candidates and actual outcomes\n', 1)[1].split('      - name: Preserve candidate and failure evidence', 1)[0]
        script = textwrap.dedent(step.split('        run: |\n', 1)[1])
        names = ['source', 'bootstrap', 'runtime', 'install', 'update', 'resolve', 'audit', 'build']
        providers = [sys.executable]
        if Path('/usr/bin/python3').is_file() and Path('/usr/bin/python3').resolve() != Path(sys.executable).resolve():
            providers.append('/usr/bin/python3')
        metadata = {provider: json.loads(subprocess.run([provider, '-I', '-c', 'import json,platform,sys;print(json.dumps([platform.python_version(),sys.executable]))'], capture_output=True, text=True, check=True).stdout) for provider in providers}
        for provider, case in product(providers, [*names, None, 'missing-evidence', 'cancelled', 'not-executed']):
            failed = case if case in names else None
            with self.subTest(provider=provider, case=case), tempfile.TemporaryDirectory() as tmp:
                outcomes = {name: 'success' for name in names}
                if failed:
                    for name in names[names.index(failed) + 1:]: outcomes[name] = 'skipped'
                    outcomes[failed] = 'failure'
                if case == 'cancelled':
                    outcomes.update(resolve='cancelled', audit='skipped', build='skipped')
                elif case == 'not-executed':
                    outcomes = dict.fromkeys(names, 'skipped')
                env = {name.upper() + '_OUTCOME': value for name, value in outcomes.items()}
                env.update(EVIDENCE_DIR=str(Path(tmp) / 'evidence'), APP_DIR=str(Path(tmp) / 'missing-app'), SOURCE_COMMIT='a' * 40)
                if case is None:
                    app = Path(env['APP_DIR']); app.mkdir()
                    (app / 'package.json').write_text('{}')
                    (app / 'package-lock.json').write_text('{}')
                subprocess.run(['/bin/bash', '-euc', script.replace('/usr/bin/python3', shlex.quote(provider), 1)], env=env, check=True, capture_output=True)
                result = json.loads((Path(env['EVIDENCE_DIR']) / 'qualification.json').read_text())
                expected = 'setup-blocked' if failed in ['source', 'bootstrap', 'runtime'] else 'executed-failure' if failed else 'qualified-build-only'
                expected = {'missing-evidence': 'evidence-missing', 'cancelled': 'cancelled', 'not-executed': 'not-executed'}.get(case, expected)
                self.assertEqual(result['state'], expected)
                self.assertEqual(result['failedStage'], failed)
                self.assertEqual(result['buildExecuted'], outcomes['build'] in ['success', 'failure'])
                self.assertFalse(result['promoted'])
                self.assertFalse(result['nativeWrites'])
                self.assertEqual(result['receiptInterpreter']['version'], metadata[provider][0])
                self.assertEqual(result['receiptInterpreter']['executable'], metadata[provider][1])
                self.assertEqual(result['receiptInterpreter']['scope'], 'receipt-only; no build or test execution')
