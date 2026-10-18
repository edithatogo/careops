"""Exercise the actual reusable job identity guard before any code checkout."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class PolicyIdentity(unittest.TestCase):
    def test_called_workflow_commit_must_match_the_tooling_commit(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/reusable-source-security.yml').read_text())
        script = workflow['jobs']['baseline']['steps'][0]['run']
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


if __name__ == '__main__':
    unittest.main()
