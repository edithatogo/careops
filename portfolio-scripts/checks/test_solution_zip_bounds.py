"""Untrusted solution packages must be bounded before decompression."""
import importlib.util
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readers():
    for name in ['clinical', 'ppg', 'clinical-package']:
        module = 'careops-ppg' if name == 'ppg' else 'clinical-hub-core'
        helper = load('bounded_' + name, f'modules/{module}/scripts/powerplatform_validation.py')
        if name == 'clinical-package':
            with patch.dict(sys.modules, {'powerplatform_validation': helper}):
                entry = load('bounded_package', f'modules/{module}/scripts/validate_solution_package.py')
            yield name, helper, entry.inspect_package
        else:
            yield name, helper, helper.inspect_zip


def archive(directory, entries, compression=0):
    path = Path(directory) / 'fictional.zip'
    with ZipFile(path, 'w', compression=compression) as target:
        for name, content in entries:
            target.writestr(name, content)
    return path


class SolutionZipBoundsTests(unittest.TestCase):
    def test_limits_reject_before_any_member_is_opened(self):
        limits = {'compressed': ('MAX_ARCHIVE_BYTES', 1),
                  'count': ('MAX_ARCHIVE_MEMBERS', 1),
                  'member': ('MAX_MEMBER_BYTES', 2),
                  'total': ('MAX_EXPANDED_BYTES', 5),
                  'ratio': ('MAX_COMPRESSION_RATIO', 2)}
        for name, helper, inspect in readers():
            for case, (setting, value) in limits.items():
                with self.subTest(reader=name, limit=case), tempfile.TemporaryDirectory() as tmp:
                    entries, compression = [('one', b'abc'), ('two', b'def')], 0
                    if case == 'ratio':
                        entries, compression = [('one', b'A' * 65536)], ZIP_DEFLATED
                    path = archive(tmp, entries, compression)
                    with patch.object(helper, setting, value), patch.object(ZipFile, 'open', side_effect=AssertionError('decompression attempted')):
                        self.assertEqual(inspect(path)['status'], 'FAIL')

    def test_duplicate_entries_rejected_before_open(self):
        for name, _, inspect in readers():
            with self.subTest(reader=name), tempfile.TemporaryDirectory() as tmp:
                with self.assertWarnsRegex(UserWarning, 'Duplicate name'):
                    path = archive(tmp, [('one', b'a'), ('one', b'b')])
                with patch.object(ZipFile, 'open', side_effect=AssertionError('decompression attempted')):
                    self.assertEqual(inspect(path)['status'], 'FAIL')

    def test_complete_bounded_reads_preserve_crc_validation(self):
        for name, helper, inspect in readers():
            with self.subTest(reader=name), tempfile.TemporaryDirectory() as tmp:
                path = archive(tmp, [('one', b'fictional')])
                self.assertEqual(helper.read_zip_members(path), {'one': b'fictional'})
                raw = bytearray(path.read_bytes())
                name_length, extra_length = struct.unpack_from('<HH', raw, 26)
                raw[30 + name_length + extra_length] ^= 1
                path.write_bytes(raw)
                with self.assertRaises(BadZipFile):
                    helper.read_zip_members(path)
                self.assertEqual(inspect(path)['status'], 'FAIL')

    def test_stream_read_is_capped_when_metadata_understates_expansion(self):
        class OversizedStream:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, limit):
                return b'x' * limit

        for name, helper, _ in readers():
            with self.subTest(reader=name), tempfile.TemporaryDirectory() as tmp:
                path = archive(tmp, [('one', b'a')])
                with patch.object(helper, 'MAX_MEMBER_BYTES', 32), patch.object(ZipFile, 'open', return_value=OversizedStream()):
                    with self.assertRaisesRegex(ValueError, 'actual_expansion'):
                        helper.read_zip_members(path)

    def test_independent_module_readers_remain_identical(self):
        paths = [ROOT / 'modules' / name / 'scripts/powerplatform_validation.py'
                 for name in ['clinical-hub-core', 'careops-ppg']]
        self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())


if __name__ == '__main__':
    unittest.main()
