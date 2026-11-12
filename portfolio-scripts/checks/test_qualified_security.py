# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0

"""Security gates reject absent coverage, changed bytes and unsafe dependency input."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('qualified',ROOT/'.careops-security/qualified_checks.py')
checks=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

class QualifiedChecks(unittest.TestCase):
    def test_asset_digest_mismatch_never_reaches_native_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'asset';path.write_bytes(b'wrong native bytes')
            with self.assertRaisesRegex(ValueError, 'digest mismatch'):checks.fetch('https://github.com/verified-fixture','0'*64,path)

    def test_review_is_bound_to_full_source_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'source.py';p.write_text('value = 1\n')
            old=checks.review_key('source.py','reviewed-rule',1,root)
            p.write_text('value = unsafe_input\n')
            self.assertNotEqual(old,checks.review_key('source.py','reviewed-rule',1,root))

    def test_missing_locks_fail_instead_of_empty_success(self):
        with patch.object(checks,'tracked',return_value=[]):
            with self.assertRaises(ValueError):checks.check_dependencies()

    def test_source_manifest_selects_each_migrated_module(self):
        paths=checks.tracked(ROOT)
        self.assertTrue(any(p.startswith('careops-approve/') and p.endswith('.py') for p in paths))
        self.assertTrue(any(p.startswith('modules/careops-process/') and p.endswith('.py') for p in paths))
        self.assertIn('careops-approve/.github/scripts/qualify-python.py',paths)

    def test_verified_download_atomically_replaces_a_racing_cache_file(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'asset'
            data = b'verified fixture bytes'
            def response(*args, **kwargs):
                destination.write_bytes(b'unverified racing cache bytes')
                value = MagicMock()
                value.__enter__.return_value.read.return_value = data
                return value
            with patch.object(checks.urllib.request, 'urlopen', side_effect=response):
                actual = checks.fetch('https://github.com/verified-fixture', checks.hashlib.sha256(data).hexdigest(), destination)
            self.assertEqual(actual, data)
            self.assertEqual(destination.read_bytes(), data)
            self.assertEqual(list(Path(folder).glob('.asset-*')), [])
