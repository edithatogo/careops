"""Synthetic one-step calibration and temporal leakage tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rims_forecast_coverage as m


class ForecastCoverageTests(unittest.TestCase):
    def setUp(self):
        self.counts = {year: 2 * (year - 2000) + 10 for year in range(2010, 2026)}

    def test_future_observation_cannot_leak_into_past_prediction(self):
        a = m.audit(self.counts)
        changed = dict(self.counts)
        changed[2024] = 99999
        b = m.audit(changed)
        self.assertEqual(a["historical_backtest"][0]["prediction"], b["historical_backtest"][0]["prediction"])
        self.assertEqual(a["historical_backtest"][2]["prediction"], b["historical_backtest"][2]["prediction"])

    def test_full_year_cutoff_excludes_provisional_count(self):
        a = m.audit(self.counts)
        b = m.audit({**self.counts, 2026: 99999})
        self.assertEqual(a["forecast_point"], b["forecast_point"])
        self.assertEqual(a["forecast_interval"], b["forecast_interval"])

    def test_linear_synthetic_series_and_nonnegative_interval(self):
        a = m.audit(self.counts)
        self.assertEqual(a["forecast_year"], 2026)
        self.assertEqual(a["selected_model"], "linear_trend")
        self.assertAlmostEqual(a["forecast_point"], 62)
        self.assertGreaterEqual(a["forecast_interval"][0], 0)
        self.assertEqual(a["backtest_years"], [2021, 2022, 2023, 2024, 2025])

    def test_missing_year_and_negative_volume_fail_closed(self):
        x = dict(self.counts)
        del x[2018]
        with self.assertRaisesRegex(ValueError, "contiguous"):
            m.audit(x)
        x = dict(self.counts)
        x[2020] = -3
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            m.audit(x)

    def test_interval_calibration_never_uses_test_year_outcome(self):
        base = m.audit(self.counts)
        x = dict(self.counts)
        x[2025] = 90000
        alt = m.audit(x)
        self.assertEqual(base["historical_backtest"][0]["interval"], alt["historical_backtest"][0]["interval"])

    def test_coverage_is_explicitly_not_accepted_as_guarantee(self):
        a = m.audit(self.counts)
        self.assertEqual(a["prequential_interval_denominator"], 5)
        self.assertNotEqual(a["interval_claim"], "validated_prospective_80_percent_prediction_interval")
        self.assertFalse("clinical" in a["interval_claim"])


if __name__ == "__main__":
    unittest.main()
