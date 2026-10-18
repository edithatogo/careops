"""Qualify actual package bytes and reject ambiguous or unsafe archive identities."""
import hashlib
import importlib.util
import json
import stat
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('artifact_sbom', Path(__file__).resolve().parents[1] / 'artifact_sbom.py')
SBOM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SBOM)


class ArtifactInventory(unittest.TestCase):
    def make(self, root, entries):
        path = Path(root) / 'release.zip'
        with warnings.catch_warnings(), zipfile.ZipFile(path, 'w') as archive:
            warnings.simplefilter('ignore', UserWarning)
            for name, data in entries:
                archive.writestr(name, data)
        return path

    def test_actual_binary_contents_and_package_digest_are_reproducible(self):
        with tempfile.TemporaryDirectory() as root:
            contents = {'solution.xml': b'<solution/>', 'assemblies/example.dll': b'\x00\x01\x02'}
            path = self.make(root, list(contents.items()))
            result = SBOM.build(path, 'Example release', 'a' * 40, 1_700_000_000)
            self.assertEqual(result, SBOM.build(path, 'Example release', 'a' * 40, 1_700_000_000))
            self.assertEqual(result['packages'][0]['checksums'][0]['checksumValue'], hashlib.sha256(path.read_bytes()).hexdigest())
            actual = {f['fileName'].removeprefix('./'): f['checksums'][0]['checksumValue'] for f in result['files']}
            self.assertEqual(actual, {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()})
            self.assertNotIn(str(Path(root)), json.dumps(result))
            self.assertEqual(len(result['relationships']), len(contents) + 1)

    def test_traversal_absolute_ambiguous_duplicate_and_empty_are_refused(self):
        cases = [[('../escape', b'x')], [('/absolute', b'x')], [('C:/absolute', b'x')], [('line\nbreak', b'x')], [('a\\b', b'x')], [('a/./b', b'x')], [('same', b'a'), ('same', b'b')], []]
        for entries in cases:
            with self.subTest(entries=entries), tempfile.TemporaryDirectory() as root:
                path = self.make(root, entries)
                with self.assertRaises(ValueError):
                    SBOM.build(path, 'Example', 'a' * 40, 1_700_000_000)

    def test_symlinks_and_excessive_content_are_refused(self):
        with tempfile.TemporaryDirectory() as root:
            entry = zipfile.ZipInfo('link')
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            path = self.make(root, [(entry, b'target')])
            with self.assertRaises(ValueError):
                SBOM.build(path, 'Example', 'a' * 40, 1_700_000_000)
            path = self.make(root, [('big', b'abcd')])
            with patch.object(SBOM, 'MAX_BYTES', 3), self.assertRaises(ValueError):
                SBOM.build(path, 'Example', 'a' * 40, 1_700_000_000)


if __name__ == '__main__':
    unittest.main()
