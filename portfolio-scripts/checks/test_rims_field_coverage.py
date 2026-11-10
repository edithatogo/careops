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
    def test_retained_fields_are_not_counted_as_used(self):
        out=module.assess("fictional",["a","b"],
            [{"source_field":"a","layer":"dashboard"},
             {"source_field":"b","layer":"retained_only"}])
        self.assertTrue(out["complete"])
        self.assertEqual(out["utilised_field_count"],1)
        self.assertEqual(out["retained_only_field_count"],1)
        self.assertTrue(out["accounted_for_not_all_utilised"])

    def test_excluded_field_needs_explicit_reason(self):
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a"],
                [{"source_field":"a","layer":"excluded"}])
        out=module.assess("fictional",["a"],
            [{"source_field":"a","layer":"excluded","reason":"synthetic rights"}])
        self.assertEqual(out["excluded_with_reason_count"],1)
        self.assertEqual(out["utilised_field_count"],0)

    def test_conflicting_exclusion_or_retained_only_refused(self):
        for prior in ("excluded","retained_only"):
            with self.subTest(prior=prior), self.assertRaises(module.CoverageError):
                module.assess("fictional",["a"],[
                    {"source_field":"a","layer":prior,
                     "reason":"synthetic rights"},
                    {"source_field":"a","layer":"dashboard"},
                ])

    def test_duplicate_projection_and_nonstring_path_refused(self):
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a"],[
                {"source_field":"a","layer":"canonical"},
                {"source_field":"a","layer":"canonical"},
            ])
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a"],[
                {"source_field":{"unhashable":"object"},"layer":"canonical"},
            ])

    def test_invalid_lineage_refused(self):
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a"],[{"source_field":"missing","layer":"dashboard"}])
    def test_duplicate_fields_refused(self):
        with self.assertRaises(module.CoverageError):
            module.assess("fictional",["a","a"],[])

if __name__=="__main__":unittest.main()
