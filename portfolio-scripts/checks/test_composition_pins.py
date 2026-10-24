"""Exercise the real portfolio gate with disposable indexes; never change source pins."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CompositionPins(unittest.TestCase):
    def run_gate(self, changed=None):
        with tempfile.TemporaryDirectory() as temporary:
            index = Path(temporary) / 'index'
            current = subprocess.check_output(['git', 'rev-parse', '--git-path', 'index'], cwd=ROOT, text=True).strip()
            shutil.copyfile(ROOT / current, index)
            env = dict(os.environ, GIT_INDEX_FILE=str(index))
            if changed:
                subprocess.run(['git', 'update-index', '--cacheinfo', '160000,' + 'a' * 40 + ',' + changed],
                               cwd=ROOT, env=env, check=True, capture_output=True)
            return subprocess.run(['pwsh', '-NoProfile', '-File', 'portfolio-scripts/Test-Portfolio.ps1'],
                                  cwd=ROOT, env=env, capture_output=True, text=True)

    def test_current_optional_composition_passes_without_initializing_children(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_independent_finance_or_process_gitlink_change_is_refused(self):
        for path in ('modules/careops-finance', 'modules/careops-process'):
            with self.subTest(path=path):
                result = self.run_gate(path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Composition gitlink does not match qualified public source', result.stderr)


if __name__ == '__main__':
    unittest.main()
