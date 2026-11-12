"""Historical, one-step publication-forecast model selection and interval audit.

Nominal interval coverage is not guaranteed: model selection and error
calibration reuse the same historical observations, with few years available.
Source Included is not independently verified CHHHS attribution.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean

MODELS = ("linear_trend", "last_year", "trailing_three_mean")


def _predict(counts: dict[int,int], year: int, model: str) -> float:
    years = sorted(y for y in counts if y < year)
    if len(years) < 5:
        raise ValueError("too few historical years")
    values = [counts[y] for y in years]
    if model == "last_year":
        return float(values[-1])
    if model == "trailing_three_mean":
        return sum(values[-3:]) / 3
    if model == "linear_trend":
        from rims_frontier_analysis import _linear
        return _linear(years, values, year)
    raise ValueError("unknown model")


def _radius(errors: list[float], nominal: float) -> float | None:
    count = len(errors)
    index = math.ceil((count + 1) * nominal)
    if count < 3 or index > count:
        return None
    return sorted(errors)[index - 1]


def audit(counts: dict[int,int], *, first_origin: int = 2021,
          last_complete: int = 2025, first_calibration_year: int = 2016,
          nominal: float = .8) -> dict:
    if not 0 < nominal < 1 or type(last_complete) is not int or last_complete > 2025:
        raise ValueError("invalid interval configuration")
    if any(type(y) is not int or type(v) is not int or v < 0 for y, v in counts.items()):
        raise ValueError("publication counts must be integer and nonnegative")
    retained = {year: value for year, value in counts.items() if year <= last_complete}
    years = sorted(retained)
    if not years or years != list(range(years[0], last_complete + 1)):
        raise ValueError("historical year range must be contiguous")
    if years[0] > first_calibration_year - 5 or first_origin <= first_calibration_year + 3 or first_origin > last_complete:
        raise ValueError("insufficient temporal calibration history")
    if last_complete < 2021 or first_calibration_year < years[0] + 5:
        raise ValueError("insufficient historical evidence")
    errors: dict[str,dict[int,float]] = {name: {} for name in MODELS}
    for year in range(first_calibration_year, last_complete + 1):
        for model in MODELS:
            errors[model][year] = abs(retained[year] - _predict(retained, year, model))
    history = []
    for year in range(first_origin, last_complete + 1):
        previous = list(range(first_calibration_year, year))
        selection_mae = {m: mean(errors[m][z] for z in previous) for m in MODELS}
        selected = min(MODELS, key=lambda m: (selection_mae[m], MODELS.index(m)))
        prediction = _predict(retained, year, selected)
        radius = _radius([errors[selected][z] for z in previous], nominal)
        interval = [max(0., prediction-radius), prediction+radius] if radius is not None else None
        history.append({
            "year": year, "selected_model": selected, "prediction": prediction,
            "actual": retained[year], "interval": interval,
            "covered": interval[0] <= retained[year] <= interval[1] if interval is not None else None,
            "calibration_years": previous, "selection_mae": selection_mae,
        })
    full = list(range(first_calibration_year, last_complete + 1))
    all_mae = {model: mean(errors[model][year] for year in full) for model in MODELS}
    winner = min(MODELS, key=lambda m: (all_mae[m], MODELS.index(m)))
    future = _predict(retained, last_complete + 1, winner)
    radius = _radius([errors[winner][year] for year in full], nominal)
    if radius is None:
        raise ValueError("not enough errors for future interval")
    evaluated = [r for r in history if r["covered"] is not None]
    return {
        "schema": "careops.rims-source-included-forecast-coverage/1",
        "source_population": "RIMS source-labelled Included, not independently validated",
        "backtest_years": [r["year"] for r in history],
        "historical_backtest": history,
        "prequential_interval_coverage": sum(bool(r["covered"]) for r in evaluated) / len(evaluated) if evaluated else None,
        "prequential_interval_denominator": len(evaluated),
        "forecast_year": last_complete + 1, "selected_model": winner,
        "forecast_point": future,
        "forecast_interval": [max(0.,future-radius),future+radius],
        "nominal_level": nominal, "model_selection_mae": all_mae,
        "interval_claim": "historically_calibrated_exploratory_not_guaranteed",
        "scientific_caveats": [
            "Only one-year-ahead errors evaluated; multi-year intervals unvalidated.",
            "Model selection and calibration reuse historical errors; coverage not guaranteed.",
            "Nonstationary ascertainment, serial dependence and small annual samples limit inference.",
            "RIMS source Included is not independent human adjudication.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with args.registry.open(encoding="utf-8-sig", newline="") as handle:
        source = list(csv.DictReader(handle))
    counts = {year: 0 for year in range(2010, 2026)}
    for row in source:
        if row.get("CanonicalKey", "").strip() and row.get("ReviewStatus", "").strip() == "Included":
            raw = row.get("PublicationYear", "").replace(",", "").strip()
            if raw.isdigit() and int(raw) in counts:
                counts[int(raw)] += 1
    output = audit(counts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("One-year forecast coverage audit completed: not an institutional forecast guarantee.")


if __name__ == "__main__":
    main()
