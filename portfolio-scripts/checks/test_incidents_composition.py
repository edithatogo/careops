"""Fail-closed source and structured-result boundaries; no private checkout needed."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('incidents', Path(__file__).resolve().parents[1] / 'qualify_incidents.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SourceBoundary(unittest.TestCase):
    def test_pin_matches_parent_inventory(self):
        self.assertEqual(MODULE.read_pin()['visibility'], 'private')

    def test_absent_checkout_is_refused(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(ValueError):
                MODULE.check_source(Path(path), 'a' * 40)

    def test_wrong_pin_and_dirty_checkout_are_refused(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path).resolve()
            def git(*args):
                return subprocess.check_output(['git', '-C', str(root), *args], text=True, stderr=subprocess.DEVNULL).strip()
            git('init', '-q')
            git('config', 'user.name', 'Fictional fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (root / 'source.txt').write_text('fictional source')
            git('add', 'source.txt')
            git('commit', '-qm', 'Fictional fixture')
            head = git('rev-parse', 'HEAD')
            MODULE.check_source(root, head)
            with self.assertRaises(ValueError):
                MODULE.check_source(root, 'a' * 40)
            (root / 'source.txt').write_text('owner work')
            with self.assertRaises(ValueError):
                MODULE.check_source(root, head)

    def test_structural_issue_cannot_hide_behind_pass_status(self):
        good = {'Status': 'Pass', 'PackageExists': True, **{k: [] for k in ['MissingRequiredPaths', 'JsonParseFailures', 'PageTreeIssues', 'SchemaIssues', 'ModelIssues']}}
        MODULE.validate_structure(good)
        for key in ['MissingRequiredPaths', 'JsonParseFailures', 'PageTreeIssues', 'SchemaIssues', 'ModelIssues']:
            with self.subTest(key=key), self.assertRaises(ValueError):
                MODULE.validate_structure({**good, key: ['fictional issue']})
            incomplete = dict(good)
            del incomplete[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                MODULE.validate_structure(incomplete)
        with self.assertRaises(ValueError):
            MODULE.validate_structure({**good, 'Status': 'Review'})


if __name__ == '__main__':
    unittest.main()
