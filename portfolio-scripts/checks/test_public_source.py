"""Regression tests for accidental publication of unreviewed or private content."""
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('public_source', ROOT / 'portfolio-scripts/validate_public_source.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicationBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = json.loads((ROOT / 'PUBLIC_SOURCE_FILES.json').read_text())
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        for name in self.manifest['files']:
            if name in self.manifest['gitlinks']:
                continue
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        self.git('add', '-f', '--', *(n for n in self.manifest['files'] if n not in self.manifest['gitlinks']))
        for name, sha in self.manifest['gitlinks'].items():
            (self.root / name).mkdir(parents=True, exist_ok=True)
            self.git('update-index', '--add', '--cacheinfo', f'160000,{sha},{name}')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def test_reviewed_snapshot_passes(self):
        self.assertEqual([], MODULE.validate(self.root))

    def test_unreviewed_file_is_refused(self):
        (self.root / 'accidental.txt').write_text('unreviewed')
        self.git('add', 'accidental.txt')
        self.assertTrue(any('inventory' in e for e in MODULE.validate(self.root)))

    def test_private_reference_is_refused(self):
        (self.root / 'README.md').write_text('Person@' + 'health.example.gov.au')
        self.assertTrue(any('Private reference' in e for e in MODULE.validate(self.root)))

    def test_missing_source_is_refused(self):
        (self.root / 'README.md').unlink()
        self.assertTrue(any('Missing or binary' in e for e in MODULE.validate(self.root)))

    def test_changed_submodule_is_refused(self):
        name = next(iter(self.manifest['gitlinks']))
        self.git('update-index', '--cacheinfo', '160000,' + 'a' * 40 + ',' + name)
        self.assertTrue(any('submodule revision' in e for e in MODULE.validate(self.root)))


if __name__ == '__main__':
    unittest.main()
