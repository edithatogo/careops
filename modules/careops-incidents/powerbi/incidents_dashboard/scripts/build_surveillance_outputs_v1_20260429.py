"""Build compact surveillance outputs for the Power BI incident dashboard.

The source incident data are low-frequency for some cohorts and overdispersed,
so this script stages empirical and overdispersion-aware signals outside Power
Query instead of relying only on generic z-score anomaly measures.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import mean, median, variance


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_CSV = PROJECT_ROOT / "data" / "cleaned_consolidated_incidents_clean_v1_20251108.csv"
OUTPUT_CSV = (
    PROJECT_ROOT
    / "powerbi"
    / "incidents_dashboard"
    / "data"
    / "surveillance_monthly_v1_20260429.csv"
)

ANALYSIS_START = date(2020, 1, 1)
ANALYSIS_END = date(2025, 12, 31)


def parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def add_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def month_range(start: date, end: date) -> list[date]:
    months: list[date] = []
    current = month_start(start)
    final = month_start(end)
    while current <= final:
        months.append(current)
        current = add_month(current)
    return months


def percentile(values: list[int], p: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * p
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return float(sorted_values[int(index)])
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def format_number(value: float | int | None, decimals: int = 4) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return f"{value:.{decimals}f}"


def text_contains_heparin(row: dict[str, str]) -> bool:
    text = " ".join(
        [
            row.get("details_clean", ""),
            row.get("summary_of_incident_clean", ""),
            row.get("investigation_and_findings", ""),
        ]
    ).lower()
    return "heparin" in text


def build_rows() -> list[dict[str, str]]:
    all_counts: Counter[date] = Counter()
    heparin_counts: Counter[date] = Counter()
    heparin_event_dates: list[date] = []
    max_source_date: date | None = None

    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            incident_date = parse_date(row.get("incident_date", ""))
            if incident_date is None:
                continue
            if max_source_date is None or incident_date > max_source_date:
                max_source_date = incident_date
            if not ANALYSIS_START <= incident_date <= ANALYSIS_END:
                continue

            incident_month = month_start(incident_date)
            all_counts[incident_month] += 1
            if text_contains_heparin(row):
                heparin_counts[incident_month] += 1
                heparin_event_dates.append(incident_date)

    if max_source_date is None:
        raise RuntimeError("No incident_date values were parsed from the source CSV.")

    months = month_range(ANALYSIS_START, min(ANALYSIS_END, max_source_date))
    last_complete_month = month_start(max_source_date)
    if max_source_date.day < 28:
        previous = date(max_source_date.year, max_source_date.month, 1)
        last_complete_month = date(previous.year - 1, 12, 1) if previous.month == 1 else date(previous.year, previous.month - 1, 1)

    heparin_intervals_by_month: dict[date, list[int]] = defaultdict(list)
    previous_heparin_date: date | None = None
    for event_date in sorted(heparin_event_dates):
        if previous_heparin_date is not None:
            heparin_intervals_by_month[month_start(event_date)].append((event_date - previous_heparin_date).days)
        previous_heparin_date = event_date

    cohort_counts = {
        "all_incidents": all_counts,
        "heparin_text_match": heparin_counts,
    }
    cohort_labels = {
        "all_incidents": "All incidents",
        "heparin_text_match": "Heparin text-match incidents",
    }

    output: list[dict[str, str]] = []
    for cohort_key, counts in cohort_counts.items():
        complete_counts = [counts[month] for month in months if month <= last_complete_month]
        expected = mean(complete_counts) if complete_counts else 0.0
        observed_variance = variance(complete_counts) if len(complete_counts) > 1 else expected
        dispersion = observed_variance / expected if expected > 0 else 0.0
        scale_sd = math.sqrt(max(observed_variance, expected, 0.0001))
        empirical_p95 = percentile(complete_counts, 0.95)
        empirical_p99 = percentile(complete_counts, 0.99)
        ucl95 = expected + 1.96 * scale_sd
        ucl99 = expected + 2.58 * scale_sd
        ewma_value = expected
        ewma_ucl = expected + 2.7 * math.sqrt(max(observed_variance, expected, 0.0001) * 0.3 / 1.7)
        cusum_value = 0.0
        cusum_k = 0.5 * scale_sd
        cusum_h = 4.0 * scale_sd
        above_median_run = 0
        baseline_median = median(complete_counts) if complete_counts else 0.0

        for month in months:
            incident_count = counts[month]
            is_partial = month > last_complete_month
            if not is_partial:
                ewma_value = 0.3 * incident_count + 0.7 * ewma_value
                cusum_value = max(0.0, cusum_value + incident_count - (expected + cusum_k))
                above_median_run = above_median_run + 1 if incident_count > baseline_median else 0

            above_empirical_p95 = (not is_partial) and incident_count > empirical_p95
            above_empirical_p99 = (not is_partial) and incident_count > empirical_p99
            above_ucl95 = (not is_partial) and incident_count > ucl95
            above_ucl99 = (not is_partial) and incident_count > ucl99
            ewma_signal = (not is_partial) and ewma_value > ewma_ucl
            cusum_signal = (not is_partial) and cusum_value > cusum_h
            run_signal = (not is_partial) and above_median_run >= 3
            signal_requires_review = any(
                [above_empirical_p95, above_empirical_p99, above_ucl95, above_ucl99, ewma_signal, cusum_signal, run_signal]
            )

            interval_values = heparin_intervals_by_month.get(month, []) if cohort_key == "heparin_text_match" else []

            output.append(
                {
                    "month_start": month.isoformat(),
                    "cohort_key": cohort_key,
                    "cohort_label": cohort_labels[cohort_key],
                    "incident_count": str(incident_count),
                    "expected_count": format_number(expected),
                    "variance_count": format_number(observed_variance),
                    "dispersion_index": format_number(dispersion),
                    "empirical_p95_limit": format_number(empirical_p95),
                    "empirical_p99_limit": format_number(empirical_p99),
                    "overdispersion_ucl_95": format_number(ucl95),
                    "overdispersion_ucl_99": format_number(ucl99),
                    "ewma_value": "" if is_partial else format_number(ewma_value),
                    "ewma_ucl": format_number(ewma_ucl),
                    "cusum_value": "" if is_partial else format_number(cusum_value),
                    "cusum_signal": str(cusum_signal).lower(),
                    "ewma_signal": str(ewma_signal).lower(),
                    "above_empirical_p95": str(above_empirical_p95).lower(),
                    "above_empirical_p99": str(above_empirical_p99).lower(),
                    "above_overdispersion_ucl_95": str(above_ucl95).lower(),
                    "above_overdispersion_ucl_99": str(above_ucl99).lower(),
                    "run_above_median_length": "" if is_partial else str(above_median_run),
                    "run_signal": str(run_signal).lower(),
                    "is_partial_month": str(is_partial).lower(),
                    "signal_requires_review": str(signal_requires_review).lower(),
                    "heparin_min_days_since_prior": str(min(interval_values)) if interval_values else "",
                    "heparin_median_days_since_prior": format_number(median(interval_values), 2) if interval_values else "",
                    "method_note": "Empirical and overdispersion-aware surveillance staging; signals require clinical review.",
                }
            )

    return output


def main() -> None:
    rows = build_rows()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} surveillance rows to {OUTPUT_CSV}")


def cli() -> None:
    global SOURCE_CSV, ANALYSIS_START, ANALYSIS_END
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--start', type=date.fromisoformat, required=True)
    parser.add_argument('--end', type=date.fromisoformat, required=True)
    args = parser.parse_args()
    if args.start > args.end:
        parser.error('Start must not follow end.')
    if not args.source.is_file():
        parser.error('Source CSV is missing.')
    SOURCE_CSV, ANALYSIS_START, ANALYSIS_END = args.source, args.start, args.end
    args.output_dir.mkdir(parents=True, exist_ok=True)
    global OUTPUT_CSV
    OUTPUT_CSV = args.output_dir / 'surveillance_monthly_v1_20260429.csv'
    if OUTPUT_CSV.exists() or OUTPUT_CSV.resolve() == SOURCE_CSV.resolve():
        parser.error('Output already exists; preserve prior output and select a new revision directory.')
    main()


if __name__ == '__main__':
    cli()
