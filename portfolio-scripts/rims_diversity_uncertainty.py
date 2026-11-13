"""Uncertainty audit for source-labelled RIMS title-theme portfolio diversity.

Publication- and year-block bootstrap intervals measure sampling variability,
not the error of the title keyword taxonomy or institutional attribution.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

Record = tuple[int, tuple[str, ...]]


def _validate(rows: list[Record]) -> list[Record]:
    result: list[Record] = []
    for year, labels in rows:
        if type(year) is not int or not 1900 <= year <= 2100:
            raise ValueError("invalid publication year")
        if not isinstance(labels, tuple) or any(not isinstance(s, str) or not s.strip() or s.strip() != s for s in labels):
            raise ValueError("invalid topic label")
        if len(labels) != len(set(labels)):
            raise ValueError("duplicate topic label")
        result.append((year, tuple(sorted(labels))))
    if not result:
        raise ValueError("empty period")
    return sorted(result)


def _diversity(rows: list[Record]) -> dict:
    fractional: dict[str, float] = defaultdict(float)
    classified = 0
    for year, labels in rows:
        if labels:
            classified += 1
            for label in labels:
                fractional[label] += 1 / len(labels)
    shares = {k: v / classified for k, v in sorted(fractional.items())} if classified else {}
    entropy = -sum(p * math.log2(p) for p in shares.values()) if classified else None
    return {
        "documents": len(rows), "classified_papers": classified,
        "classified_share": classified / len(rows),
        "effective_themes": 2 ** entropy if entropy is not None else None,
        "fractional_theme_shares": shares,
    }


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    location = (len(ordered) - 1) * probability
    lower, upper = math.floor(location), math.ceil(location)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (location - lower)


def _resample_years(rows: list[Record], rng: random.Random) -> list[Record]:
    groups: dict[int, list[Record]] = defaultdict(list)
    for row in rows:
        groups[row[0]].append(row)
    years = sorted(groups)
    return [r for _ in years for r in groups[years[rng.randrange(len(years))]]]


def compare(old: list[Record], recent: list[Record], *, repetitions: int = 2000, seed: int = 20261113) -> dict:
    if type(repetitions) is not int or not 100 <= repetitions <= 200000:
        raise ValueError("invalid repetitions")
    if type(seed) is not int:
        raise ValueError("invalid seed")
    a, b = _validate(old), _validate(recent)
    if set(y for y, _ in a) & set(y for y, _ in b):
        raise ValueError("periods overlap")
    da, db = _diversity(a), _diversity(b)
    if da["effective_themes"] is None or db["effective_themes"] is None:
        raise ValueError("classified records required")
    rng = random.Random(seed)
    draws = {"paper": [], "year": []}
    cover = {"paper": [], "year": []}
    for _ in range(repetitions):
        for kind in ("paper", "year"):
            if kind == "paper":
                aa = [a[rng.randrange(len(a))] for _ in a]
                bb = [b[rng.randrange(len(b))] for _ in b]
            else:
                aa, bb = _resample_years(a, rng), _resample_years(b, rng)
            x, y = _diversity(aa), _diversity(bb)
            if x["effective_themes"] is None or y["effective_themes"] is None:
                continue
            draws[kind].append(y["effective_themes"] - x["effective_themes"])
            cover[kind].append(y["classified_share"] - x["classified_share"])
    def summary(kind: str) -> dict:
        vals = draws[kind]
        if not vals:
            raise ValueError("no valid bootstrap draws")
        return {
            "draws": len(vals),
            "requested_draws": repetitions,
            "undefined_draws": repetitions - len(vals),
            "interval_95": [_percentile(vals, .025), _percentile(vals, .975)],
            "coverage_difference_interval_95": [_percentile(cover[kind], .025), _percentile(cover[kind], .975)],
            "share_change_positive": sum(v > 0 for v in vals) / len(vals),
        }
    paper, block = summary("paper"), summary("year")
    paper["sampling_assumption"] = "Independent publications; may understate correlated yearly effects."
    block["years_per_period"] = {"old": len(set(y for y, _ in a)), "recent": len(set(y for y, _ in b))}
    block["sampling_assumption"] = "Year block resampling; few years, secular trends and variable annual volumes limit inference."
    return {
        "schema": "careops.rims-title-diversity-uncertainty/1",
        "source_cohort": "RIMS source-labelled Included, no independent institutional approval",
        "old": da, "recent": db,
        "observed_effective_theme_difference": db["effective_themes"] - da["effective_themes"],
        "classified_share_difference": db["classified_share"] - da["classified_share"],
        "paper_bootstrap": paper, "year_block_bootstrap": block,
        "independently_approved_institutional_cohort": False,
        "seed": seed,
        "caveats": [
            "Title heuristic labels are unvalidated and may overlap.",
            "Resampling intervals do not account for affiliation or taxonomy errors.",
            "Difference is not proof of disciplinary diversification.",
        ],
    }


def _labels(title: str) -> tuple[str, ...]:
    from rims_frontier_analysis import TOPICS
    return tuple(k for k, pat in TOPICS.items() if re.search(pat, title.lower()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=2000)
    args = parser.parse_args()
    with args.registry.open(encoding="utf-8-sig", newline="") as stream:
        source = list(csv.DictReader(stream))
    rows: list[Record] = []
    for row in source:
        if row.get("CanonicalKey", "").strip() and row.get("ReviewStatus", "").strip() == "Included":
            year = row.get("PublicationYear", "").replace(",", "").strip()
            if re.fullmatch(r"(?:19|20)\d{2}", year):
                rows.append((int(year), _labels(row.get("Title", ""))))
    result = compare([r for r in rows if 2010 <= r[0] <= 2017],
                     [r for r in rows if 2018 <= r[0] <= 2025],
                     repetitions=args.repetitions)
    result["source_rulebook"] = "rims_frontier_analysis.TOPICS, same commit"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("Source-qualified title diversity resampling completed; not a validated taxonomy.")


if __name__ == "__main__":
    main()
