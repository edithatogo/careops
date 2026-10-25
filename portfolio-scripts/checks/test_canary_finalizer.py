"""Keep scheduled Python runtime previews disabled by policy."""
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class CanaryFinalizer(unittest.TestCase):
    def test_scheduled_python_runtime_preview_jobs_are_absent(self):
        paths = (
            ROOT / '.github/workflows/development-canary.yml',
            ROOT / '.github/workflows/clinical-hub-candidate.yml',
        )
        for path in paths:
            with self.subTest(workflow=path.name):
                workflow = yaml.safe_load(path.read_text())
                jobs = workflow['jobs']
                self.assertNotIn('runtime', jobs)
                for name, job in jobs.items():
                    for step in job.get('steps', []):
                        if str(step.get('uses', '')).startswith('actions/setup-python@'):
                            self.assertEqual(step['with']['python-version'], '3.15.1', f'{path.name}:{name}')
                            self.assertNotIn('allow-prereleases', step.get('with', {}), f'{path.name}:{name}')


if __name__ == '__main__':
    unittest.main()
