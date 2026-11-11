# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Read-only accreditation *application* coverage, not accreditation judgements.

Reuse the versioned PPG accreditation graph; no new source of authority, evidence
store, licence requirement, network request or native write. Missing assessments,
unreviewed mappings and unpublished editions remain explicitly unresolved.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path

from scripts.ppg_accreditation_contract import REQUIREMENT_KINDS, validate_graph

_OPERATIVE = {"published"}
_REVIEWED = {"reviewed"}


def _as_of(value: str) -> str:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("as_of must be an explicit ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("as_of must be an explicit ISO date") from error
    if parsed.isoformat() != value:
        raise ValueError("as_of must be an explicit ISO date")
    return value


def project_coverage(graph: dict, review_context_key: str, scope_key: str, *,
                     kinds: tuple[str, ...], as_of: str) -> dict:
    """Project coverage by exact framework edition, requirement and service scope.

    A PPG mapping indicates a potential relationship, not implementation. Human
    assessment status indicates a recorded human act, not an external assessor's
    rating, a verified operation or an accreditation outcome.
    """
    validation = validate_graph(graph)
    as_of = _as_of(as_of)
    if (not isinstance(review_context_key, str) or not review_context_key.strip()
            or not isinstance(scope_key, str) or not scope_key.strip()
            or not isinstance(kinds, tuple) or not kinds
            or any(not isinstance(kind, str) or kind not in REQUIREMENT_KINDS for kind in kinds)
            or len(kinds) != len(set(kinds))):
        raise ValueError("Explicit context, scope and supported requirement kinds required")
    contexts = {c["ReviewContextKey"]: c for c in graph["contexts"]}
    context = contexts.get(review_context_key)
    if context is None or scope_key not in context["ScopeKeys"]:
        raise ValueError("Review context does not include selected scope")
    frameworks = {r["FrameworkKey"]: r for r in graph["frameworks"]}
    selected_requirements = sorted(
        [r for r in graph["requirements"] if r["FrameworkKey"] in context["FrameworkKeys"]
         and r["kind"] in kinds],
        key=lambda row: (row["FrameworkKey"], row["RequirementKey"]))
    assessments = {}
    for a in graph["assessments"]:
        if a["ReviewContextKey"] != review_context_key or a["ScopeKey"] != scope_key:
            continue
        identity = a["RequirementKey"]
        if identity in assessments:
            raise ValueError("Duplicate assessment for same context/requirement/scope")
        assessments[identity] = a
    records = []
    for requirement in selected_requirements:
        key = requirement["RequirementKey"]
        edition = frameworks[requirement["FrameworkKey"]]
        assessment = assessments.get(key)
        if assessment is not None and assessment.get("decidedAt") is not None:
            try:
                decision_instant = datetime.fromisoformat(
                    assessment["decidedAt"].replace("Z", "+00:00"))
            except (ValueError, TypeError, AttributeError) as error:
                raise ValueError("Invalid human decision timestamp") from error
            if decision_instant.tzinfo is None or decision_instant.utcoffset() is None:
                raise ValueError("Human decision must have timezone")
            if decision_instant.date() > date.fromisoformat(as_of):
                raise ValueError("Human decision is after as_of")
        related = sorted(
            [m for m in graph["mappings"] if m["RequirementKey"] == key
             and m["ReviewContextKey"] == review_context_key and m["ScopeKey"] == scope_key],
            key=lambda m: m["MappingKey"])
        # Assessments select specific mapping versions; other contextual
        # relationships cannot silently certify the selected assessment.
        selected_mapping_keys = set(assessment["MappingKeys"]) if assessment else set()
        if assessment is not None:
            active = [m for m in related if m["MappingKey"] in selected_mapping_keys]
        else:
            active = related
        if not active:
            mapping_coverage = "none"
        elif all(m["reviewState"] in _REVIEWED for m in active):
            mapping_coverage = "reviewed"
        elif all(m["reviewState"] == "proposed" for m in active):
            mapping_coverage = "proposed-only"
        else:
            mapping_coverage = "mixed-or-unresolved"
        if edition["status"] not in _OPERATIVE:
            readiness = "nonoperative-edition"
        elif assessment is None:
            readiness = "assessment-missing"
        elif assessment["applicability"] == "unknown":
            readiness = "applicability-unresolved"
        elif assessment["applicability"] == "not-applicable":
            readiness = "not-applicable-recorded"
        elif assessment["outcome"] == "unknown":
            readiness = "human-assessment-pending"
        elif mapping_coverage != "reviewed":
            readiness = "evidence-review-pending"
        else:
            readiness = "human-review-recorded"
        records.append({
            "RequirementKey": key,
            "FrameworkKey": requirement["FrameworkKey"],
            "editionStatus": edition["status"],
            "requirementKind": requirement["kind"],
            "ReviewContextKey": review_context_key,
            "ScopeKey": scope_key,
            "AssessmentKey": assessment["AssessmentKey"] if assessment else None,
            "mappingKeys": [m["MappingKey"] for m in related],
            "mappingCoverage": mapping_coverage,
            "applicability": assessment["applicability"] if assessment else "unknown",
            "internalReviewOutcome": assessment["outcome"] if assessment else "unknown",
            "readiness": readiness,
            "sourceCurrency": "not-independently-verified",
            "implementationObserved": None,
            "accreditationStatus": None,
        })
    summary = Counter(row["readiness"] for row in records)
    return {
        "contractVersion": 1,
        "asOf": as_of,
        "ReviewContextKey": review_context_key,
        "ScopeKey": scope_key,
        "selectedKinds": sorted(kinds),
        "graphSha256": validation["graphSha256"],
        "requirements": records,
        "counts": {kind: summary[kind] for kind in sorted(summary)},
        "mappingDoesNotEstablishImplementation": True,
        "evidenceDoesNotEstablishCompliance": True,
        "acceptanceTransferred": False,
        "sourceBytesVerified": False,
        "externalAccreditationDecision": None,
        "nativeWrites": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--kind", action="append", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite existing review result")
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    projection = project_coverage(graph, args.context, args.scope,
                                  kinds=tuple(args.kind), as_of=args.as_of)
    # Review inputs and outputs may be sensitive: leave them out of Git.
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(projection, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"graphSha256": projection["graphSha256"],
                      "counts": projection["counts"], "nativeWrites": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
