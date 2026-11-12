"""Tests for title-theme sampling uncertainty and source-authority boundaries."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rims_diversity_uncertainty as m


class DiversityUncertaintyTests(unittest.TestCase):
    def test_repeatable_and_order_invariant(self):
        old = [(2010, ("a",)), (2011, ("a", "b")), (2012, ()), (2013, ("b",))]
        recent = [(2020, ("a",)), (2021, ("b",)), (2022, ("c",)), (2023, ("a", "c"))]
        a = m.compare(old, recent, repetitions=200, seed=123)
        self.assertEqual(a, m.compare(list(reversed(old)), list(reversed(recent)), repetitions=200, seed=123))
        self.assertEqual(a["paper_bootstrap"]["requested_draws"], 200)

    def test_fractional_effect_and_classification_rate(self):
        a = m.compare([(2010, ("a",)), (2011, ())],
                      [(2020, ("a",)), (2021, ("b",))], repetitions=100)
        self.assertEqual(a["old"]["classified_share"], .5)
        self.assertEqual(a["recent"]["classified_share"], 1.)
        self.assertEqual(a["classified_share_difference"], .5)
        self.assertAlmostEqual(a["observed_effective_theme_difference"], 1.)

    def test_rejects_empty_or_overlapping_periods(self):
        with self.assertRaisesRegex(ValueError, "classified"):
            m.compare([(2010, ())], [(2020, ("b",))], repetitions=100)
        with self.assertRaisesRegex(ValueError, "overlap"):
            m.compare([(2010, ("a",))], [(2010, ("b",))], repetitions=100)

    def test_invalid_year_duplicate_labels_and_draws_fail(self):
        with self.assertRaises(ValueError):
            m.compare([(0, ("a",))], [(2020, ("b",))], repetitions=100)
        with self.assertRaises(ValueError):
            m.compare([(2010, ("a", "a"))], [(2020, ("b",))], repetitions=100)
        with self.assertRaises(ValueError):
            m.compare([(2010, ("a",))], [(2020, ("b",))], repetitions=10)

    def test_resample_source_authority_not_promoted(self):
        z = m.compare([(2010, ("a",)), (2011, ("b",))],
                      [(2020, ("a",)), (2021, ("b",))], repetitions=100)
        self.assertFalse(z["independently_approved_institutional_cohort"])
        self.assertEqual(z["year_block_bootstrap"]["years_per_period"], {"old": 2, "recent": 2})
        self.assertEqual(len(z["paper_bootstrap"]["interval_95"]), 2)

    def test_uses_canonical_topic_rulebook(self):
        previous = sys.modules.get("rims_frontier_analysis")
        sys.modules["rims_frontier_analysis"] = SimpleNamespace(TOPICS={"marker": r"rare-marker-xy"})
        try:
            self.assertEqual(m._labels("rare-marker-xy study"), ("marker",))
        finally:
            if previous is None:
                del sys.modules["rims_frontier_analysis"]
            else:
                sys.modules["rims_frontier_analysis"] = previous


if __name__ == "__main__":
    unittest.main()
