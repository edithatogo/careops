"""Synthetic tests for CHHHS title-theme portfolio diversity."""
import importlib.util
from pathlib import Path
import unittest

module_path = Path(__file__).resolve().parents[1] / "rims_frontier_diversity.py"
spec = importlib.util.spec_from_file_location("rims_frontier_diversity", module_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestDiversity(unittest.TestCase):
    def test_fractional_topic_diversity_pure_single_theme(self):
        result = m.diversity([("a",), ("a",), ("a",)])
        self.assertEqual(result["entropy_bits"], 0)
        self.assertEqual(result["effective_themes"], 1)
        self.assertEqual(result["classified_papers"], 3)

    def test_multi_label_fractional_allocation(self):
        result = m.diversity([("a", "b"), ("b",), ()])
        self.assertEqual(result["classified_papers"], 2)
        self.assertEqual(result["unclassified_papers"], 1)
        self.assertAlmostEqual(result["fractional_theme_shares"]["a"], .25)
        self.assertAlmostEqual(result["fractional_theme_shares"]["b"], .75)

    def test_permutation_is_order_invariant(self):
        a = [("a", "b"), ("c",), (), ("a",)]
        self.assertEqual(m.diversity(a), m.diversity(list(reversed(a))))

    def test_blank_or_duplicates_raise(self):
        with self.assertRaises(ValueError):
            m.diversity([("a", "a")])
        with self.assertRaises(ValueError):
            m.diversity([(" ",)])

    def test_no_theme_yields_null_entropy(self):
        a = m.diversity([(), ()])
        self.assertIsNone(a["entropy_bits"])
        self.assertEqual(a["unclassified_papers"], 2)

    def test_relative_change_has_denominator_and_disclaimer(self):
        x = m.temporal_comparison([("a",), ("b",)], [("a",), ("a",), ("a",), ("b",)])
        self.assertAlmostEqual(x["old"]["fractional_theme_shares"]["a"], .5)
        self.assertAlmostEqual(x["recent"]["fractional_theme_shares"]["a"], .75)
        self.assertEqual(x["method"], "fractional assignment within each keyword-classified title; no independent validation")


if __name__ == "__main__":
    unittest.main()
