"""Measured Finance coverage must retain missed code and propagate fixture failure."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is required for breakpoint instrumentation')
class MeasuredFinanceCoverage(unittest.TestCase):
    def test_real_hit_miss_and_failed_fixture(self):
        for fail in (False, True):
            with self.subTest(failing_fixture=fail), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'scripts').mkdir()
                (root / 'tests').mkdir()
                (root / 'scripts/source.ps1').write_text('param([bool] $Selected)\nif ($Selected) {\n $value = 1\n} else {\n $value = 2\n}\n$value\n')
                body = "throw 'fictional fixture failure'" if fail else "& (Join-Path $PSScriptRoot '../scripts/source.ps1') -Selected $true | Out-Null"
                (root / 'tests/Test-Probe.ps1').write_text(body)
                output = root / 'coverage/lcov.info'
                run = subprocess.run(['pwsh', '-NoProfile', '-File', str(ROOT / 'modules/careops-finance/scripts/Generate-LcovCoverage.ps1'), '-RootPath', tmp, '-OutputPath', str(output)], capture_output=True, text=True, timeout=60)
                if fail:
                    self.assertNotEqual(run.returncode, 0)
                    self.assertFalse(output.exists())
                else:
                    self.assertEqual(run.returncode, 0, run.stderr)
                    report = output.read_text(encoding='utf-8-sig')
                    self.assertIn('DA:3,1', report)
                    self.assertIn('DA:5,0', report)
