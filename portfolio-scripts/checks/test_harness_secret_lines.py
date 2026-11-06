"""Exercise the actual harness against fictional Git publication boundaries."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is required to execute the actual harness')
class HarnessSecretLines(unittest.TestCase):
    def test_blank_values_do_not_consume_following_lines_and_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            harness = root / 'harness'
            harness.mkdir()
            shutil.copyfile(ROOT / 'harness/Test-Harness.ps1', harness / 'Test-Harness.ps1')
            (harness / 'policy.json').write_text(json.dumps({
                'name': 'fictional secret-line regression', 'required': [],
                'forbiddenTrackedPrefixes': [], 'workflowFiles': [],
                'allowContentsWrite': False,
            }))
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for key in ('CLIENT_SECRET', 'ACCESS_TOKEN', 'REFRESH_TOKEN', 'PASSWORD'):
                for ending in ('\n', '\r\n'):
                    for populated in (False, True):
                        with self.subTest(key=key, ending=repr(ending), populated=populated):
                            value = ('fictional' + '-value') if populated else ''
                            (root / 'sample.env').write_bytes(
                                (key + '=\t' + value + ending + '# Next line is documentation.' + ending).encode()
                            )
                            result = subprocess.run(
                                ['pwsh', '-NoProfile', '-File', str(harness / 'Test-Harness.ps1')],
                                cwd=root, capture_output=True, text=True,
                            )
                            self.assertEqual(result.returncode == 0, not populated, result.stdout + result.stderr)
