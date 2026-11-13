"""Pure reference statistics for a separately approved silent registration pilot.

This library does not establish external source independence, cohort
representativeness, clinical effectiveness, staff entitlement or authorisation.
All inputs are fictional in public source and require source-owner acceptance.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import sqrt
from typing import Any


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _wilson(numerator: int, denominator: int) -> tuple[float, float] | None:
    """Approximate two-sided 95% Wilson interval; no false 100% at tiny n."""
    if denominator == 0:
        return None
    z = 1.959963984540054
    p = numerator / denominator
    z2 = z * z
    middle = (p + z2 / (2 * denominator)) / (1 + z2 / denominator)
    radius = (z / (1 + z2 / denominator)) * sqrt(
        (p * (1 - p) / denominator) + z2 / (4 * denominator * denominator)
    )
    return (max(0.0, middle - radius), min(1.0, middle + radius))


def summarise_evaluation(
    rows: Sequence[Mapping[str, Any]], *, sampling_design: str,
    sampling_frame_verified: bool = False,
) -> dict[str, Any]:
    """Count only independently verified classifications; preserve abstentions.

    Sampling-frame verification is a trusted caller assertion, not inferred
    from a string label. Real deployment requires signed source provenance,
    sampling design, independent adjudication and owner acceptance.
    """
    if type(sampling_frame_verified) is not bool:
        raise ValueError("sampling_frame_verified must be Boolean")
    if sampling_design not in ("representative", "enriched", "convenience"):
        raise ValueError("sampling_design must be explicit")
    cases = list(rows)
    seen: set[str] = set()
    matrix = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    unverified = 0
    abstained = 0
    verified = 0
    for case in cases:
        key = case.get("engagementRef")
        if not isinstance(key, str) or not key.strip() or key in seen:
            raise ValueError("engagementRef must be nonempty and unique")
        seen.add(key)
        truth = case.get("materialChange")
        alert = case.get("emittedAlert")
        approved = case.get("independentlyVerified")
        if truth is not None and type(truth) is not bool:
            raise ValueError("materialChange must be Boolean or unknown")
        if alert is not None and type(alert) is not bool:
            raise ValueError("emittedAlert must be Boolean or abstain")
        if type(approved) is not bool:
            raise ValueError("independentlyVerified must be Boolean")
        if approved and (not isinstance(case.get("referenceRef"), str)
                         or not case["referenceRef"].strip()):
            raise ValueError("verified outcome requires independent evidence reference")
        if not approved or truth is None:
            unverified += 1
            continue
        verified += 1
        if alert is None:
            abstained += 1
            continue
        label = "tp" if truth and alert else "fn" if truth else "fp" if alert else "tn"
        matrix[label] += 1
    tp, fp, fn, tn = (matrix[k] for k in ("tp", "fp", "fn", "tn"))
    precision = _rate(tp, tp + fp)
    sensitivity = _rate(tp, tp + fn)
    specificity = _rate(tn, tn + fp)
    complete = bool(cases) and verified == len(cases) and abstained == 0
    prevalence_qualified = sampling_design == "representative" and sampling_frame_verified and complete
    return {
        "eligible": len(cases), "adjudicated": verified, "unverified": unverified,
        "abstained": abstained, "counts": matrix, "samplingDesign": sampling_design,
        "precision": precision, "sensitivity": sensitivity, "specificity": specificity,
        "precision95CI": _wilson(tp, tp + fp),
        "sensitivity95CI": _wilson(tp, tp + fn),
        "specificity95CI": _wilson(tn, tn + fp),
        "prevalenceQualified": prevalence_qualified,
        "populationPrevalence": _rate(tp + fn, len(cases)) if prevalence_qualified else None,
        "adjudicationCoverage": _rate(verified, len(cases)),
        "classificationCoverage": _rate(tp + fp + fn + tn, len(cases)),
        "notes": (
            "Source-only statistics; independent truth, sampling-frame verification, "
            "clinical thresholds and operational acceptance remain external."
        ),
    }
