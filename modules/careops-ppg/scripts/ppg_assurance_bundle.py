# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Combine existing PPG graph overlays into one *read-only* assurance packet.

No new authoritative store, automatic real tasks, clinical conclusion, external
accreditation rating or native Microsoft operation. Everything remains scoped to
one known review context, service and as-of date. Review candidates are prompts
for a human owner to decide, not issued actions or an assertion of a deficiency.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.ppg_assurance_coverage import project_coverage
from scripts.ppg_obligation_application import project_obligations
from scripts.ppg_evidence_currency import project_currency


def assemble_bundle(graph, *, profiles, adoptions, receipts,
                    context_key, scope_key, as_of, kinds):
    coverage = project_coverage(graph, context_key, scope_key,
                                kinds=kinds, as_of=as_of)
    obligations = project_obligations(graph, profiles, adoptions, context_key,
                                      scope_key, as_of=as_of)
    currency = project_currency(graph, receipts, context_key, scope_key,
                                as_of=as_of)
    hashes = {x["graphSha256"] for x in (coverage, obligations, currency)}
    if len(hashes) != 1:
        raise ValueError("Source graphs differ across assurance projections")
    obligation_by_requirement = {
        row["RequirementKey"]: row for row in obligations["requirements"]
    }
    currency_by_version = {
        row["EvidenceVersionKey"]: row for row in currency["evidence"]
    }
    linked_evidence = {}
    for row in graph["mappings"]:
        if row["ReviewContextKey"] != context_key or row["ScopeKey"] != scope_key:
            continue
        linked_evidence.setdefault(row["RequirementKey"], set()).add(
            row["EvidenceVersionKey"])

    review_tasks = []
    def candidate(requirement, reason):
        review_tasks.append({
            "ReviewContextKey": context_key,
            "ScopeKey": scope_key,
            "RequirementKey": requirement,
            "reason": reason,
            "state": "candidate-only",
            "ownerRef": None,
            "authorityVerified": False,
            "actionIssued": False,
        })

    for row in coverage["requirements"]:
        key = row["RequirementKey"]
        related = obligation_by_requirement[key]
        # A draft/unpublished framework is a future-transition candidate; it is
        # not added to the operative accreditation work queue by this projection.
        if row["readiness"] == "nonoperative-edition":
            continue
        if row["readiness"] == "assessment-missing":
            candidate(key, "assessment-missing")
        elif row["readiness"] == "applicability-unresolved":
            candidate(key, "applicability-unresolved")
        if row["mappingCoverage"] != "reviewed":
            candidate(key, "mapping-review-pending")
        if related["localAdoption"] == "unobserved":
            candidate(key, "local-adoption-unobserved")
        versions = linked_evidence.get(key, set())
        if not versions or any(
                currency_by_version[version]["reviewWindow"] != "within-review-window"
                for version in versions):
            candidate(key, "evidence-source-unverified")

    review_tasks.sort(key=lambda x: (x["RequirementKey"], x["reason"]))
    return {
        "contractVersion": 1,
        "asOf": as_of,
        "ReviewContextKey": context_key,
        "ScopeKey": scope_key,
        "graphSha256": next(iter(hashes)),
        "coverage": coverage,
        "obligations": obligations,
        "currency": currency,
        "candidateReviewTasks": review_tasks,
        "tasksCreated": False,
        "complianceCertified": False,
        "sourceAuthorityVerified": False,
        "externalAccreditationDecision": None,
        "nativeWrites": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--adoptions", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--kind", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to replace a prior review bundle")
    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    profiles = json.loads(args.profiles.read_text(encoding="utf-8"))
    adoptions = json.loads(args.adoptions.read_text(encoding="utf-8"))
    receipts = json.loads(args.receipts.read_text(encoding="utf-8"))
    output = assemble_bundle(
        graph, profiles=profiles, adoptions=adoptions, receipts=receipts,
        context_key=args.context, scope_key=args.scope,
        as_of=args.as_of, kinds=tuple(args.kind),
    )
    # No automatic circulation. The result is for an approved private record
    # location and must not be committed with operational evidence.
    import os
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(args.output, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(output, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({
        "graphSha256": output["graphSha256"],
        "candidateCount": len(output["candidateReviewTasks"]),
        "nativeWrites": 0,
    }))


if __name__ == "__main__":
    main()
