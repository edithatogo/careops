"""Bounded, safe XML parsing for the dataset-lineage manifest builder."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path



SCRIPT = Path(__file__).resolve().parents[1] / "scripts/ppg_dataset_lineage.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("ppg_dataset_lineage", SCRIPT)
lineage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lineage)


class DatasetLineageXmlTests(unittest.TestCase):
    def parse_bytes(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.xml"
            path.write_bytes(data)
            return lineage._parse_xml(path)

    def test_preserves_declared_xml_encoding(self):
        root = self.parse_bytes(
            b'<?xml version="1.0" encoding="ISO-8859-1"?><Value>caf\xe9</Value>'
        )
        self.assertEqual(root.tag, "Value")
        self.assertEqual(root.text, "caf\N{LATIN SMALL LETTER E WITH ACUTE}")

    def test_rejects_xml_larger_than_bounded_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.xml"
            path.write_bytes(b" " * (lineage.MAX_XML_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "exceeds"):
                lineage._parse_xml(path)

    def test_rejects_utf16_doctype(self):
        payload = '<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE root><root/>'
        with self.assertRaisesRegex(ValueError, "DTD"):
            self.parse_bytes(payload.encode("utf-16"))

    def test_rejects_doctype_without_entities(self):
        with self.assertRaisesRegex(ValueError, "DTD"):
            self.parse_bytes(b'<!DOCTYPE root><root/>')

    def test_rejects_doctype_and_entity_declarations(self):
        payload = b'<!DOCTYPE root [<!ENTITY value "expanded">]><root>&value;</root>'
        with self.assertRaisesRegex(ValueError, "DTD"):
            self.parse_bytes(payload)


if __name__ == "__main__":
    unittest.main()
