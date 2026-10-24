"""Exercise submission acceptance and complete graph readback without network writes."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = yaml.safe_load((ROOT / '.github/workflows/dependency-inventory.yml').read_text())
STEPS = WORKFLOW['jobs']['inventory']['steps']


def python_block(name):
    script = next(step['run'] for step in STEPS if step.get('name') == name)
    return script.split("python - <<'PYCODE'\n", 1)[1].split('\nPYCODE', 1)[0]


class HostedInventory(unittest.TestCase):
    def run_block(self, name, files):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path, content in files.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(content))
            return subprocess.run([sys.executable, '-c', python_block(name)], cwd=root, capture_output=True, text=True)

    def test_write_job_is_main_only_and_has_no_pull_request_trigger(self):
        events = WORKFLOW.get('on', WORKFLOW.get(True))
        self.assertEqual(set(events), {'push', 'workflow_dispatch'})
        self.assertEqual(events['push']['branches'], ['main'])
        self.assertEqual(WORKFLOW['jobs']['inventory']['if'], "github.ref == 'refs/heads/main'")
        self.assertFalse(WORKFLOW['concurrency']['cancel-in-progress'])
        checkout = next(step for step in STEPS if step.get('uses', '').startswith('actions/checkout@'))
        self.assertFalse(checkout['with']['persist-credentials'])

    def test_submission_requires_explicit_success_and_retained_id(self):
        for result, success in [({'result': 'SUCCESS', 'id': 123}, True), ({'result': 'FAILURE', 'id': 123}, False), ({'result': 'SUCCESS'}, False)]:
            with self.subTest(result=result):
                run = self.run_block('Submit once and require server acceptance', {'.local/dependency-inventory/submission.json': result})
                self.assertEqual(run.returncode == 0, success, run.stderr)

    def test_graph_readback_refuses_missing_or_wrong_versions(self):
        package = 'pkg:pypi/example@1.0'
        snapshot = {'manifests': {'requirements-ci.lock': {'resolved': {package: {'package_url': package}}}}}
        for observed, success in [(package, True), ('pkg:pypi/example@0.9', False), ('pkg:pypi/other@1.0', False)]:
            with self.subTest(observed=observed):
                graph = {'sbom': {'packages': [{'externalRefs': [{'referenceType': 'purl', 'referenceLocator': observed}]}]}}
                run = self.run_block('Read back the current dependency graph', {'.local/dependency-inventory/snapshot.json': snapshot, '.local/dependency-inventory/graph.json': graph})
                self.assertEqual(run.returncode == 0, success, run.stderr)

    def test_actual_lock_guard_rejects_missing_extra_and_changed_packages(self):
        for packages, success in [([('alpha', '1.0')], True), ([], False), ([('alpha', '0.9')], False), ([('alpha', '1.0'), ('extra', '1.0')], False)]:
            with self.subTest(packages=packages), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / 'requirements-ci.lock').write_text('alpha==1.0\n')
                prefix = "import importlib.metadata, types\nimportlib.metadata.distributions = lambda: [types.SimpleNamespace(metadata={'Name': n}, version=v) for n, v in " + repr(packages) + "]\n"
                run = subprocess.run([sys.executable, '-c', prefix + python_block('Require installed versions to match the complete hash lock')], cwd=root, capture_output=True, text=True)
                self.assertEqual(run.returncode == 0, success, run.stderr)

    def test_raw_inspect_paths_are_excluded_from_retained_artifact(self):
        artifact = STEPS[-1]
        self.assertNotIn('inspect.json', artifact['with']['path'])
        self.assertIn('submission.json', artifact['with']['path'])
        self.assertIn('!cancelled()', artifact['if'])


if __name__ == '__main__':
    unittest.main()
