"""Build aggregate health-concept extraction outputs for Power BI.

This is a deterministic lexicon-based staging pass. It exposes only aggregate
counts by month and concept category, not raw narrative text or incident-level
extracts.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_CSV = PROJECT_ROOT / "data" / "cleaned_consolidated_incidents_clean_v1_20251108.csv"
CONCEPT_OUTPUT_CSV = (
    PROJECT_ROOT / "powerbi" / "incidents_dashboard" / "data" / "health_concept_monthly_v1_20260429.csv"
)
QA_OUTPUT_CSV = PROJECT_ROOT / "powerbi" / "incidents_dashboard" / "data" / "health_concept_qa_v1_20260429.csv"
DICTIONARY_OUTPUT_CSV = (
    PROJECT_ROOT / "powerbi" / "incidents_dashboard" / "data" / "health_concept_dictionary_v1_20260429.csv"
)

ANALYSIS_START = date(2020, 1, 1)
ANALYSIS_END = date(2025, 12, 31)

CONCEPTS: dict[str, dict[str, list[str]]] = {
    "medication": {
        "Medication safety": ["medication", "medicine", "dose", "dosage", "drug", "prescribing", "administration"],
        "Anticoagulation and heparin": ["heparin", "anticoag", "clexane", "enoxaparin", "warfarin", "apixaban", "rivaroxaban"],
    },
    "vascular_procedure": {
        "Vascular/procedure context": ["vascular", "catheter", "cannula", "line", "picc", "central line", "procedure", "surgery"],
    },
    "monitoring_lab": {
        "Monitoring/lab terms": ["aptt", "inr", "platelet", "haemoglobin", "hemoglobin", "blood test", "pathology", "monitoring"],
    },
    "transfer_handover": {
        "Transfer/handover": ["handover", "transfer", "discharge", "handoff", "referral", "escalation call"],
    },
    "deterioration_escalation": {
        "Deterioration/escalation": ["deterioration", "deteriorated", "rapid response", "met call", "icu", "resuscitation", "sepsis"],
    },
    "device_line": {
        "Device/line": ["device", "pump", "infusion", "drip", "line", "tube", "drain", "catheter"],
    },
    "documentation_process": {
        "Documentation/process": ["documentation", "documented", "policy", "protocol", "checklist", "communication", "delay", "missed"],
    },
}

REDACTION_HINTS = ["@", "dob", "mrn", "date of birth", "phone", "mobile", "address", "incident number"]
AMBIGUOUS_TERMS = ["line", "transfer", "delay", "missed", "normal"]


def parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def month_start(value: date) -> str:
    return date(value.year, value.month, 1).isoformat()


def normalize_text(row: dict[str, str]) -> str:
    text = " ".join(
        [
            row.get("details_clean", ""),
            row.get("summary_of_incident_clean", ""),
            row.get("investigation_and_findings", ""),
        ]
    ).lower()
    return re.sub(r"\s+", " ", text)


def contains_term(text: str, term: str) -> bool:
    if " " in term:
        return term in text
    return re.search(rf"\b{re.escape(term)}\b", text) is not None


def bool_text(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "y"}


def build_outputs() -> None:
    concept_counts: Counter[tuple[str, str, str, str]] = Counter()
    heparin_overlap_counts: Counter[tuple[str, str, str, str]] = Counter()
    high_harm_overlap_counts: Counter[tuple[str, str, str, str]] = Counter()
    qa = {
        "records_processed": 0,
        "records_with_concepts": 0,
        "redaction_hint_records": 0,
        "ambiguous_term_records": 0,
    }
    monthly_processed: Counter[str] = Counter()
    monthly_with_concepts: Counter[str] = Counter()

    with SOURCE_CSV.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            incident_date = parse_date(row.get("incident_date", ""))
            if incident_date is None or not ANALYSIS_START <= incident_date <= ANALYSIS_END:
                continue
            month = month_start(incident_date)
            text = normalize_text(row)
            qa["records_processed"] += 1
            monthly_processed[month] += 1
            has_redaction_hint = any(hint in text for hint in REDACTION_HINTS)
            has_ambiguous_term = any(contains_term(text, term) for term in AMBIGUOUS_TERMS)
            if has_redaction_hint:
                qa["redaction_hint_records"] += 1
            if has_ambiguous_term:
                qa["ambiguous_term_records"] += 1

            matched_any = False
            is_heparin = "heparin" in text
            is_high_harm = row.get("harm_severity_category", "") == "High Harm"
            for category, labels in CONCEPTS.items():
                for label, terms in labels.items():
                    if any(contains_term(text, term) for term in terms):
                        key = (month, category, label, "Lexicon")
                        concept_counts[key] += 1
                        if is_heparin:
                            heparin_overlap_counts[key] += 1
                        if is_high_harm:
                            high_harm_overlap_counts[key] += 1
                        matched_any = True

            if matched_any:
                qa["records_with_concepts"] += 1
                monthly_with_concepts[month] += 1

    CONCEPT_OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with CONCEPT_OUTPUT_CSV.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "month_start",
                "concept_category",
                "concept_label",
                "extraction_method",
                "record_count",
                "heparin_text_match_count",
                "high_harm_count",
                "review_status",
                "limitation_note",
            ],
        )
        writer.writeheader()
        for key, record_count in sorted(concept_counts.items()):
            writer.writerow(
                {
                    "month_start": key[0],
                    "concept_category": key[1],
                    "concept_label": key[2],
                    "extraction_method": key[3],
                    "record_count": record_count,
                    "heparin_text_match_count": heparin_overlap_counts[key],
                    "high_harm_count": high_harm_overlap_counts[key],
                    "review_status": "Analyst review",
                    "limitation_note": "Rule-based aggregate extraction; no raw narrative text exposed.",
                }
            )

    with QA_OUTPUT_CSV.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["metric_key", "metric_label", "metric_value", "metric_note"])
        writer.writeheader()
        for key, label in [
            ("records_processed", "Records processed"),
            ("records_with_concepts", "Records with at least one extracted concept"),
            ("redaction_hint_records", "Records with identifier/redaction hints"),
            ("ambiguous_term_records", "Records with ambiguous terms"),
        ]:
            writer.writerow(
                {
                    "metric_key": key,
                    "metric_label": label,
                    "metric_value": qa[key],
                    "metric_note": "Aggregate QA only; inspect source narratives outside the report under approved governance.",
                }
            )
        writer.writerow(
            {
                "metric_key": "months_processed",
                "metric_label": "Months processed",
                "metric_value": len(monthly_processed),
                "metric_note": "Uses the explicitly selected analysis period.",
            }
        )

    with DICTIONARY_OUTPUT_CSV.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=["concept_category", "concept_label", "term", "inclusion_status", "governance_note"],
        )
        writer.writeheader()
        for category, labels in CONCEPTS.items():
            for label, terms in labels.items():
                for term in terms:
                    writer.writerow(
                        {
                            "concept_category": category,
                            "concept_label": label,
                            "term": term,
                            "inclusion_status": "Included",
                            "governance_note": "Lexicon term requires clinical review before production decision-support use.",
                        }
                    )

    print(f"Wrote {sum(concept_counts.values())} aggregate concept matches to {CONCEPT_OUTPUT_CSV}")
    print(f"Wrote QA metrics to {QA_OUTPUT_CSV}")
    print(f"Wrote concept dictionary to {DICTIONARY_OUTPUT_CSV}")


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
    global CONCEPT_OUTPUT_CSV, QA_OUTPUT_CSV, DICTIONARY_OUTPUT_CSV
    CONCEPT_OUTPUT_CSV = args.output_dir / 'health_concept_monthly_v1_20260429.csv'
    QA_OUTPUT_CSV = args.output_dir / 'health_concept_qa_v1_20260429.csv'
    DICTIONARY_OUTPUT_CSV = args.output_dir / 'health_concept_dictionary_v1_20260429.csv'
    if any(p.exists() or p.resolve() == SOURCE_CSV.resolve() for p in [CONCEPT_OUTPUT_CSV, QA_OUTPUT_CSV, DICTIONARY_OUTPUT_CSV]):
        parser.error('Output already exists; preserve prior output and select a new revision directory.')
    build_outputs()


if __name__ == '__main__':
    cli()
