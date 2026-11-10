"""Synthetic field lineage completeness regression tests."""
import importlib.util
from pathlib import Path
import unittest
path=Path(__file__).resolve().parents[1]/"rims_field_coverage.py"
spec=importlib.util.spec_from_file_location("rims_field_coverage",path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FieldCoverageTests(unittest.TestCase):
    def test_missing_field_is_visible(self):
        result=module.assess("fictional",["a","b"],[{"source_field":"a","layer":"dashboard"}])
        self.assertEqual(result["unassessed_fields"],["b"])
        self.assertFalse(result["complete"])
    def test_retained_only_not_dashboard_usage(self):
        result=module.assess("fictional",["a"],[{"source_field":"a","layer":"retained_only"}])
        self.assertTrue(result["complete"])
        self.assertEqual(result["fields_by_layer"]["dashboard"],0)
        self.assertFalse(result["native_parity_verified"])
    def test_invalid_lineage_refused(self):
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a"],[{"source_field":"missing","layer":"dashboard"}])
    def test_duplicate_fields_refused(self):
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a","a"],[])

if __name__=="__main__":unittest.main()
