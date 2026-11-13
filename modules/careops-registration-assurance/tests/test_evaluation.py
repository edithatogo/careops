"""Synthetic silent-evaluation regression tests; no staff records or live API."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from registration_assurance.evaluation import summarise_evaluation  # noqa: E402


def sample(ref: str, truth: bool | None, alert: bool | None, *,
           verified: bool = True) -> dict[str, object]:
    return {
        "engagementRef": ref,
        "independentlyVerified": verified,
        "referenceRef": "test:independent" if verified else None,
        "materialChange": truth,
        "emittedAlert": alert,
    }


class SilentEvaluationTests(unittest.TestCase):
    def test_qualified_confusion_matrix_and_metrics(self) -> None:
        cases = [
            sample("test:e1", True, True), sample("test:e2", False, False),
            sample("test:e3", True, False), sample("test:e4", False, True),
        ]
        result = summarise_evaluation(
            cases, sampling_design="representative", sampling_frame_verified=True,
        )
        self.assertEqual(result["counts"], {"tp": 1, "fp": 1, "fn": 1, "tn": 1})
        self.assertEqual((result["precision"], result["sensitivity"], result["specificity"]),
                         (0.5, 0.5, 0.5))
        self.assertTrue(result["prevalenceQualified"])

    def test_sampling_label_alone_cannot_establish_population_prevalence(self) -> None:
        result = summarise_evaluation(
            [sample("test:e1", True, True), sample("test:e2", False, False)],
            sampling_design="representative",
        )
        self.assertFalse(result["prevalenceQualified"])
        self.assertIsNone(result["populationPrevalence"])

    def test_no_positive_reference_cases_never_claim_perfect_sensitivity(self) -> None:
        result = summarise_evaluation([sample("test:e1", False, False)],
                                      sampling_design="representative")
        self.assertIsNone(result["sensitivity"])
        self.assertIsNone(result["sensitivity95CI"])

    def test_zero_missed_events_still_has_nonzero_upper_error_uncertainty(self) -> None:
        result = summarise_evaluation([sample("test:e1", True, True)],
                                      sampling_design="representative")
        lower, upper = result["sensitivity95CI"]
        self.assertLess(lower, 1.0)
        self.assertEqual(upper, 1.0)

    def test_unverified_truth_is_not_a_false_negative(self) -> None:
        result = summarise_evaluation([
            sample("test:e1", True, False, verified=False),
            sample("test:e2", False, False),
        ], sampling_design="representative")
        self.assertEqual(result["counts"]["fn"], 0)
        self.assertEqual(result["unverified"], 1)

    def test_abstention_not_automatically_classified_as_negative(self) -> None:
        result = summarise_evaluation([
            sample("test:e1", True, None), sample("test:e2", False, False),
        ], sampling_design="representative")
        self.assertEqual(result["counts"]["fn"], 0)
        self.assertEqual(result["abstained"], 1)
        self.assertIsNone(result["sensitivity"])

    def test_duplicate_engagement_cannot_inflate_denominator(self) -> None:
        with self.assertRaises(ValueError):
            summarise_evaluation([
                sample("test:e1", True, True), sample("test:e1", False, False),
            ], sampling_design="representative")

    def test_verified_outcome_requires_independent_reference(self) -> None:
        bad = sample("test:e1", True, False)
        bad["referenceRef"] = ""
        with self.assertRaises(ValueError):
            summarise_evaluation([bad], sampling_design="representative")

    def test_enriched_sampling_does_not_claim_population_prevalence(self) -> None:
        result = summarise_evaluation([
            sample("test:e1", True, True), sample("test:e2", True, False),
        ], sampling_design="enriched", sampling_frame_verified=True)
        self.assertFalse(result["prevalenceQualified"])
        self.assertIsNone(result["populationPrevalence"])

    def test_empty_cohort_reports_unknown_ratios_and_zero_eligible(self) -> None:
        result = summarise_evaluation([], sampling_design="representative")
        self.assertEqual(result["eligible"], 0)
        self.assertIsNone(result["precision"])
        self.assertIsNone(result["sensitivity"])
        self.assertIsNone(result["adjudicationCoverage"])

    def test_truth_and_alert_must_not_be_coerced(self) -> None:
        for bad in ("yes", 1, 0):
            with self.subTest(bad=bad):
                item = sample("test:e1", True, True)
                item["materialChange"] = bad
                with self.assertRaises(ValueError):
                    summarise_evaluation([item], sampling_design="representative")

    def test_invalid_sampling_frame_qualification_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            summarise_evaluation([sample("test:e1", True, True)],
                                  sampling_design="representative",
                                  sampling_frame_verified="yes")


if __name__ == "__main__":
    unittest.main()
