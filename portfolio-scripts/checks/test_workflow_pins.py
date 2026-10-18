"""Prevent mutable remote execution references in shared and module workflows."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('workflow_pins', Path(__file__).resolve().parents[1] / 'check_workflow_pins.py')
PINS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PINS)


class WorkflowPins(unittest.TestCase):
    def test_remote_commit_local_workflow_and_image_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workflow = root / '.github/workflows/ci.yml'
            workflow.parent.mkdir(parents=True)
            for ref, valid in [('actions/checkout@' + 'a' * 40, True), ('org/repo/.github/workflows/ci.yml@' + 'b' * 40, True), ('docker://alpine@sha256:' + 'c' * 64, True), ('$/.github/workflows/ci.yml', True), ('./.github/actions/local', True), ('actions/checkout@v7', False), ('org/repo/.github/workflows/ci.yml@main', False), ('docker://alpine:latest', False)]:
                workflow.write_text('jobs:\n  test:\n    steps:\n      - uses: ' + ref + '\n')
                with self.subTest(ref=ref):
                    self.assertEqual(not PINS.check(root), valid)


if __name__ == '__main__':
    unittest.main()
