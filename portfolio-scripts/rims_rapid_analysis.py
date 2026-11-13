"""Reproducible, fail-closed source-labelled CHHHS publication reporting.

The user's accepted CSV is private input and must never be checked into Git.
All results are descriptive SOURCE-INCLUDED, not independently reviewed
institutional research. OpenAlex citation observations are optional and
source-specific; they cannot be summed with any other provider's numbers.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from statistics import median
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

THEMES = {
    "Tropical / infectious diseases": r"melioidosis|leptospir|dengue|malaria|snakebite|antivenom|envenomat|rickettsi|q fever|mosquito|tuberculosis|infection|sepsis|infectious|buruli|ulcerans",
    "First Nations / equity": r"aboriginal|torres strait|indigenous|first nations|health equity|cultural safety|remote communit",
    "Intensive care / emergency": r"intensive care|critical care|resuscitation|emergency department|trauma|anaesthe|anesthe|ventilat|cardiac arrest|ecmo",
    "Cancer / haematology": r"cancer|carcinom|lymphom|leuk[a-z]*emia|tumou?r|oncolog|melanom|myelom|chemotherap",
    "Surgery / procedural care": r"surgic|surgery|operative|laparoscop|colorectal|endoscop|cholecyst|arthroplast|orthopaed|vascular",
    "Ageing / dementia": r"dementia|cognitive|aging|ageing|geriatric|older person|elderly",
    "Maternal / child / reproductive": r"pregnan|neonat|paediatric|pediatric|maternal|obstetric|birth|contracept|fertility|breastfeed|cerebral palsy",
    "Health services / implementation": r"health service|implementation|hospital flow|quality improvement|cost.effect|budget impact|service deliver|models? of care|workforce|telehealth|health econom|care pathway",
}


def normalize_doi(value: Any) -> str:
    s = str(value or "").strip().lower()
    s = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/", "", s)
    return s if s.startswith("10.") and "/" in s and not any(c.isspace() for c in s) else ""


def normalize_pmid(value: Any) -> str:
    s = str(value or "").strip()
    return s if s.isascii() and s.isdigit() and int(s) > 0 else ""


def publication_year(value: Any) -> int | None:
    s = str(value or "").strip().replace(",", "")
    if not re.fullmatch(r"\d{4}", s):
        return None
    y = int(s)
    return y if 1900 <= y <= 2026 else None


def classify_affiliation(raw: str) -> str:
    text = re.sub(r"\s+", " ", str(raw)).lower()
    if "mareeba" in text and ("adelaide" in text or "babies' hospital" in text or "babies hospital" in text):
        return "nonlocal_false_positive"
    if re.search(r"cairns\s*(?:and|&)\s*hinterland|\bchhhs\b|cairns health service district", text):
        return "hhs_affiliation_candidate"
    facilities = r"cairns(?:\s+base|\s+district)?\s+hospital|atherton hospital|mareeba hospital|innisfail hospital|tully hospital|mossman hospital|gordonvale hospital|herberton hospital|babinda hospital"
    if re.search(facilities, text):
        return "hospital_affiliation_candidate"
    return "unresolved"


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def profile_registry(registry: list[dict[str, str]], *, openalex: list[dict[str, str]] | None = None) -> dict[str, Any]:
    rows = list(registry)
    keyed = [r for r in rows if str(r.get("CanonicalKey", "")).strip()]
    source_included = [r for r in keyed if r.get("ReviewStatus", "").strip() == "Included"]
    states = Counter(r.get("ReviewStatus", "").strip() or "(blank)" for r in rows)
    keys = [r["CanonicalKey"].strip() for r in keyed]
    years = Counter()
    invalid_year = 0
    for r in source_included:
        y = publication_year(r.get("PublicationYear", ""))
        if y is None:
            invalid_year += 1
        else:
            years[str(y)] += 1
    dois = defaultdict(list)
    invalid_doi = 0
    invalid_pmid = 0
    for r in keyed:
        raw_doi = str(r.get("DOI", "")).strip()
        raw_pmid = str(r.get("PMID", "")).strip()
        d = normalize_doi(raw_doi)
        if raw_doi and not d:
            invalid_doi += 1
        if raw_pmid and not normalize_pmid(raw_pmid):
            invalid_pmid += 1
        if d:
            dois[d].append(r["CanonicalKey"].strip())
    topics = Counter()
    no_theme = 0
    for r in source_included:
        title = r.get("Title", "").lower()
        labels = [k for k, pat in THEMES.items() if re.search(pat, title)]
        if not labels:
            no_theme += 1
        topics.update(labels)
    result: dict[str, Any] = {
        "schema": "careops.rims-rapid-bibliometrics/1",
        "claim_scope": "source-labelled Included, never independent review or CHHHS employment",
        "rows": len(rows), "keyed": len(keyed), "keyless": len(rows) - len(keyed),
        "distinct_canonical_keys": len(set(keys)), "duplicate_canonical_key_rows": len(keys) - len(set(keys)),
        "states_all_rows": dict(sorted(states.items())),
        "source_included": len(source_included), "source_needs_review_keyed": sum(r.get("ReviewStatus", "").strip() == "Needs Review" for r in keyed),
        "independently_approved": 0,
        "yearly_source_included": dict(sorted(years.items())),
        "source_included_invalid_year": invalid_year,
        "first_year_source_included": min(map(int, years)) if years else None,
        "provisional_year": 2026,
        "duplicate_doi_groups": sum(len(v) > 1 for v in dois.values()),
        "duplicate_doi_rows": sum(len(v) for v in dois.values() if len(v) > 1),
        "invalid_doi_count": invalid_doi, "invalid_pmid_count": invalid_pmid,
        "theme_method": "overlapping title keyword rules, not manually verified disciplines",
        "source_included_theme_mentions": dict(sorted(topics.items(), key=lambda a: (-a[1], a[0]))),
        "source_included_unclassified_themes": no_theme,
        "citation_graph_edges": None,
        "caveats": ["Source Included is not independent human approval", "2026 partial publication year", "Topic labels overlap and require manual validation", "Citation counts source/vintage-specific, not provider-additive"],
    }
    if openalex is not None:
        lookup: dict[str, int] = {}
        conflict = set()
        for r in openalex:
            doi = normalize_doi(r.get("doi", ""))
            if not doi:
                continue
            try:
                value = int(str(r.get("cited_by_count", "")).strip())
                if value < 0:
                    continue
            except (ValueError, TypeError):
                continue
            if doi in lookup:
                conflict.add(doi)
            else:
                lookup[doi] = value
        citation_counts = [lookup[d] for r in source_included if (d := normalize_doi(r.get("DOI", ""))) and d in lookup and d not in conflict]
        result.update({
            "openalex_duplicate_key_count": len(conflict),
            "openalex_citation_coverage_source_included": len(citation_counts),
            "openalex_source_included_citation_sum": sum(citation_counts),
            "openalex_source_included_citation_median": median(citation_counts) if citation_counts else None,
            "openalex_count_snapshot": "caller_source_vintage_unverified",
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--openalex", type=Path, help="Optional OpenAlex discovery CSV; not an adjudicated cohort")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = profile_registry(read_csv(args.registry), openalex=read_csv(args.openalex) if args.openalex else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.output}; {result['source_included']} source-labelled publications")


if __name__ == "__main__":
    main()
