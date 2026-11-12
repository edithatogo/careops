"""Prevent parity qualification from hiding missing or changed solution content."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location('package_compare', Path(__file__).parents[2] / 'powerplatform/scripts/compare_solution_packages.py')
COMPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARE)


class PackageParityTests(unittest.TestCase):
    def test_only_entity_collection_order_is_ignored(self):
        first = b'<Entity><Name>a</Name><controls><control id="1"/><control id="2"/></controls></Entity>'
        second = b'<Entity><Name>b</Name></Entity>'
        def document(entities):
            return b'<ImportExportXml><Entities>' + entities + b'</Entities></ImportExportXml>'
        original = document(first + second)
        self.assertEqual(COMPARE.xml_shape(original), COMPARE.xml_shape(document(second + first)))
        changed = first.replace(b'<control id="1"/><control id="2"/>', b'<control id="2"/><control id="1"/>')
        self.assertNotEqual(COMPARE.xml_shape(original), COMPARE.xml_shape(document(changed + second)))

    def test_changed_field_value_is_not_normalized(self):
        self.assertNotEqual(COMPARE.xml_shape(b'<field required="true"/>'), COMPARE.xml_shape(b'<field required="false"/>'))

    def test_duplicate_entity_identity_is_rejected(self):
        with self.assertRaises(AssertionError):
            COMPARE.xml_shape(b'<ImportExportXml><Entities><Entity><Name>a</Name></Entity><Entity><Name>a</Name></Entity></Entities></ImportExportXml>')

    def test_unsafe_archive_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'unsafe.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('../solution.xml', '<solution/>')
            with self.assertRaises(AssertionError):
                COMPARE.members(path)

    def test_all_binary_member_bytes_are_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'solution.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('asset.bin', b'\x00\x01\xff')
            self.assertEqual(COMPARE.members(path), {'asset.bin': b'\x00\x01\xff'})
