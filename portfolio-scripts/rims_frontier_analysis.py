"""Source-labelled scientometric topic evolution and forecast backtests.

No source-labelled Included record is promoted to independently reviewed.
No field-normalised or causal impact claim is made. Pure stdlib.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

TOPICS = {
    "tropical_infectious": r"melioidosis|leptospirosis|dengue|malaria|snakebite|antivenom|envenomat|rickettsi|q fever|mosquito|tuberculosis|infection|sepsis|buruli",
    "first_nations": r"aboriginal|torres strait|indigenous|first nations|health equity|cultural safety",
    "emergency_critical_care": r"intensive care|critical care|resuscitation|emergency department|trauma|anaesthe|anesthe|ventilat|cardiac arrest|ecmo",
    "cancer": r"cancer|carcinom|lymphom|leuk[a-z]*emia|tumou?r|oncolog|melanom|myelom|chemotherap",
    "surgery": r"surgic|surgery|operative|laparoscop|colorectal|endoscop|cholecyst|arthroplast|orthopaed|vascular",
    "ageing": r"dementia|cognitive|aging|ageing|geriatric|older person|elderly",
    "maternal_child": r"pregnan|neonat|paediatric|pediatric|maternal|obstetric|birth|contracept|fertility|breastfeed|cerebral palsy",
    "health_services": r"health service|implementation|hospital flow|quality improvement|cost.effect|budget impact|service deliver|workforce|telehealth|health econom|care pathway",
}


def read_records(path: str | Path) -> list[dict[str,str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _year(text: str) -> int | None:
    value = str(text or "").strip().replace(",", "")
    return int(value) if re.fullmatch(r"(?:19|20)\d\d", value) else None


def _labels(text: str) -> tuple[str, ...]:
    return tuple(topic for topic, pattern in TOPICS.items() if re.search(pattern, str(text or "").lower()))


def _linear(years: list[int], values: list[int], target: int) -> float:
    x0 = sum(years)/len(years)
    y0 = sum(values)/len(values)
    den = sum((x-x0)**2 for x in years)
    slope = sum((x-x0)*(y-y0) for x,y in zip(years, values))/den if den else 0.
    return max(0., y0+slope*(target-x0))


def backtest(counts: dict[int,int], *, first_test: int, last_test: int) -> dict:
    """Rolling-origin one-step evaluation; only training years precede prediction."""
    scores: dict[str,list[float]] = {name: [] for name in ("last_year", "trailing_three_mean", "linear_trend")}
    forecasts: list[dict] = []
    for target in range(first_test, last_test+1):
        train = [year for year in sorted(counts) if year < target]
        if len(train) < 5 or target not in counts:
            continue
        y = [counts[year] for year in train]
        methods = {
            "last_year": float(y[-1]),
            "trailing_three_mean": sum(y[-3:])/3,
            "linear_trend": _linear(train, y, target),
        }
        forecasts.append({"year":target, "actual":counts[target], "predictions":{k:round(v,3) for k,v in methods.items()}})
        for name,pred in methods.items():
            scores[name].append(abs(pred-counts[target]))
    if len(forecasts)<3:
        raise ValueError("at least three out-of-sample evaluation years required")
    return {
        "window": [first_test,last_test],
        "rolling_predictions": forecasts,
        "mean_absolute_error": {key: round(sum(vals)/len(vals),3) for key,vals in scores.items()},
        "best_by_mae": min(scores, key=lambda k:sum(scores[k])/len(scores[k])),
        "warning": "Retrospective source-labelled counts; evaluation does not validate future citation coverage, indexing drift or causal effect.",
    }


def analyse(rows: list[dict[str,str]], *, end_complete_year:int=2025) -> dict:
    if not 1900 <= end_complete_year <= 2100:
        raise ValueError("invalid complete year")
    included = [row for row in rows if row.get("CanonicalKey","").strip() and row.get("ReviewStatus","").strip()=="Included"]
    counts = Counter()
    periods = {"2010-2017": Counter(), "2018-2025": Counter()}
    pair_counts = {k:Counter() for k in periods}
    unclassified = Counter()
    for item in included:
        year=_year(item.get("PublicationYear",""))
        if year is None or year>end_complete_year:
            continue
        counts[year]+=1
        span = "2010-2017" if 2010<=year<=2017 else "2018-2025" if 2018<=year<=2025 else None
        if not span:
            continue
        labels = _labels(item.get("Title",""))
        if not labels:
            unclassified[span]+=1
        for label in labels:
            periods[span][label]+=1
        for i,a in enumerate(labels):
            for b in labels[i+1:]:
                pair_counts[span]["|".join(sorted((a,b)))]+=1
    if not any(counts.values()):
        raise ValueError("no eligible source-labelled publications")
    bt=backtest({y:counts[y] for y in range(2010,end_complete_year+1)}, first_test=2018,last_test=end_complete_year)
    return {
        "schema":"careops.rims-frontier-observatory/1",
        "cohort":"RIMS source-labelled Included, not independently reviewed",
        "included_all_years":len(included),
        "complete_year_cutoff":end_complete_year,
        "annual":{str(k):v for k,v in sorted(counts.items())},
        "topic_rulebook":"titles-only; multi-label overlapping heuristic, not semantic or validated research taxonomy",
        "period_denominators":{k:sum(counts[y] for y in range(2010,2018) if k=="2010-2017")+sum(counts[y] for y in range(2018,2026) if k=="2018-2025") for k in periods},
        "topic_counts":{k:dict(v) for k,v in periods.items()},
        "pair_counts":{k:dict(v) for k,v in pair_counts.items()},
        "unclassified":dict(unclassified),
        "forecasts_backtest":bt,
        "field_normalised_impact":None,
        "disruption_index":None,
        "population_need_alignment":None,
        "methodological_notes":[
            "Classifications represent publication titles, not calibrated topics or healthcare service quality.",
            "Co-occurrence counts are within-document two-theme pairs, not bibliographic coupling or citation co-occurrence.",
            "Forecast models cannot be accepted without prospective/out-of-period validation; compare reference baselines.",
            "The source register's Included status has no independently supplied reviewer authority.",
        ],
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--registry",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    obj=analyse(read_records(args.registry))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Analysed source-labelled RIMS publication trends and topic evolution; withheld unsupported impact metrics.")


if __name__=="__main__":
    main()
