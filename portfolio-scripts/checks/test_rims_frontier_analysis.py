"""Synthetic tests for CHHHS frontier observable analysis."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location("rims_frontier_analysis",Path(__file__).resolve().parents[1]/"rims_frontier_analysis.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def record(key,year,title="Melioidosis and intensive care",status="Included"):
    return {"CanonicalKey":key,"PublicationYear":str(year),"ReviewStatus":status,"Title":title}


class FrontierTests(unittest.TestCase):
    def setUp(self):
        self.rows=[record(str(y),y) for y in range(2010,2026)]

    def test_no_automatic_review_or_impact_claim(self):
        result=mod.analyse(self.rows)
        self.assertEqual(result["included_all_years"],16)
        self.assertIsNone(result["field_normalised_impact"])
        self.assertIsNone(result["disruption_index"])

    def test_title_multilabel_pairs(self):
        result=mod.analyse(self.rows)
        self.assertEqual(result["topic_counts"]["2018-2025"]["tropical_infectious"],8)
        self.assertEqual(result["pair_counts"]["2018-2025"]["emergency_critical_care|tropical_infectious"],8)

    def test_excludes_keyless_and_unverified_status(self):
        rows=self.rows+[record("",2024),record("candidate",2024,status="Needs Review")]
        result=mod.analyse(rows)
        self.assertEqual(result["included_all_years"],16)

    def test_provisional_year_excluded(self):
        result=mod.analyse(self.rows+[record("future",2026)])
        self.assertEqual(result["included_all_years"],17)
        self.assertNotIn("2026",result["annual"])

    def test_backtest_no_future_information(self):
        values={y:5 if y<2020 else 200 for y in range(2010,2026)}
        results=mod.backtest(values,first_test=2018,last_test=2025)
        p2019=next(x for x in results["rolling_predictions"] if x["year"]==2019)
        self.assertEqual(p2019["predictions"]["last_year"],5)
        self.assertEqual(p2019["predictions"]["linear_trend"],5)

    def test_backtest_errors_stated(self):
        values={y:(y-2000)*4 for y in range(2010,2026)}
        results=mod.backtest(values,first_test=2018,last_test=2025)
        self.assertLess(results["mean_absolute_error"]["linear_trend"],1e-6)
        self.assertGreater(results["mean_absolute_error"]["last_year"],0)


if __name__=="__main__":unittest.main()
