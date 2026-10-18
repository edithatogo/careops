"""Bounded generative fuzzing of source-only configuration validation."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from hypothesis import example, given, settings, strategies as st

SPEC = importlib.util.spec_from_file_location('delivery', Path(__file__).resolve().parents[1] / 'validate_delivery.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
settings.register_profile('ci', max_examples=200, deadline=None, derandomize=True, print_blob=True)
settings.load_profile('ci')
SCALAR = st.none() | st.booleans() | st.integers() | st.text(max_size=40)
JSON = st.recursive(SCALAR, lambda child: st.lists(child, max_size=4) | st.dictionaries(st.text(max_size=15), child, max_size=4), max_leaves=15)


def profile():
    return {'schemaVersion': 1, 'module': 'fictional', 'sourceKind': 'portfolio', 'releasePolicy': 'development-first-verified-promotion', 'standards': 'https://github.com/edithatogo/careops/blob/main/docs/development-and-delivery.md', 'localGuide': 'guide.md', 'nextTasks': [{'id': 'one', 'status': 'queued', 'operation': 'fictional', 'success': 'fixture', 'lane': 'local', 'tools': ['local']}]}


class DeliveryFuzz(unittest.TestCase):
    def validate(self, value):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            (root / '.careops').mkdir()
            (root / 'guide.md').write_text('fictional guide')
            (root / '.careops/module.json').write_text(json.dumps(value))
            errors = MODULE.validate(root)
            self.assertIsInstance(errors, list)
            self.assertTrue(all(isinstance(error, str) for error in errors))
            return errors

    @given(JSON)
    def test_arbitrary_json_returns_diagnostics(self, value):
        self.validate(value)

    @given(JSON)
    @example([])
    @example({})
    def test_source_kind_types_fail_closed(self, kind):
        data = profile()
        data['sourceKind'] = kind
        errors = self.validate(data)
        if not isinstance(kind, str) or kind not in {'portfolio', 'reusable-source', 'implementation', 'migration-toolkit', 'historical-implementation'}:
            self.assertIn('invalid sourceKind', errors)

    @given(JSON)
    @example([])
    @example({})
    def test_status_types_fail_closed(self, status):
        data = profile()
        data['nextTasks'][0]['status'] = status
        errors = self.validate(data)
        if not isinstance(status, str) or status not in {'queued', 'in-progress', 'blocked', 'complete'}:
            self.assertTrue(any('invalid task status' in error for error in errors))

    @given(st.text(max_size=40))
    def test_duplicate_task_ids_are_refused(self, task_id):
        data = profile()
        data['nextTasks'][0]['id'] = task_id
        data['nextTasks'] *= 2
        self.assertIn('task IDs must be nonempty and unique', self.validate(data))

    @given(st.sampled_from(['../outside.md', '/outside.md', 'C:\\outside.md', '\\\\server\\share\\outside.md', 'bad\0name']))
    def test_unsafe_guide_paths_are_refused(self, guide):
        data = profile()
        data['localGuide'] = guide
        self.assertTrue(any('localGuide' in error for error in self.validate(data)))

    def test_symlink_guide_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as path:
            parent = Path(path)
            root = parent / 'repo'
            (root / '.careops').mkdir(parents=True)
            outside = parent / 'outside.md'
            outside.write_text('private fixture')
            (root / 'guide.md').symlink_to(outside)
            (root / '.careops/module.json').write_text(json.dumps(profile()))
            self.assertTrue(any('localGuide' in error for error in MODULE.validate(root)))


if __name__ == '__main__':
    unittest.main()
