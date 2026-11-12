# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Read-only source review-window projection for existing PPG evidence versions.

A valid receipt is an asserted source-capture reference, not verification of its
underlying bytes, current policy authority, observed implementation or
accreditation. A stale review window never turns into a failing accreditation
rating. Real source material remains in its owning records service.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
import re

from scripts.ppg_accreditation_contract import validate_graph

_SHA256 = re.compile(r"[a-f0-9]{64}\Z")


def _date(value, field):
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("Invalid "+field)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Invalid "+field) from error
    if parsed.isoformat() != value:
        raise ValueError("Invalid "+field)
    return parsed


def project_currency(graph, receipts, context_key, scope_key, *, as_of):
    """Evaluate explicit review-date claims against exact mapped evidence versions.

    No attempt is made to extrapolate source recency from document creation,
    infer an approved source or derive an assessor's rating.
    """
    validation = validate_graph(graph)
    today = _date(as_of, "as_of")
    if not isinstance(receipts, list) or any(not isinstance(row, dict) for row in receipts):
        raise ValueError("Receipt list of objects required")
    contexts = {row["ReviewContextKey"]: row for row in graph["contexts"]}
    context = contexts.get(context_key)
    if context is None or scope_key not in context["ScopeKeys"]:
        raise ValueError("Review context scope mismatch")
    evidence_versions = {row["EvidenceVersionKey"]: row for row in graph["evidenceVersions"]}
    mapped_versions = {
        row["EvidenceVersionKey"] for row in graph["mappings"]
        if row["ReviewContextKey"] == context_key and row["ScopeKey"] == scope_key
    }
    by_version = {}
    for receipt in receipts:
        key = receipt.get("EvidenceVersionKey")
        if not isinstance(key, str) or key not in evidence_versions:
            raise ValueError("Receipt evidence version unknown")
        if key in by_version:
            raise ValueError("Duplicate source-capture receipt")
        if key not in mapped_versions:
            raise ValueError("Receipt version outside selected context/scope")
        source = evidence_versions[key]
        for own, supplied in (("sourceSystem", "SourceSystem"),
                              ("sourceKey", "SourceKey"),
                              ("sourceVersion", "SourceVersion")):
            if receipt.get(supplied) != source.get(own):
                raise ValueError("Receipt source identity mismatch")
        ref = receipt.get("CaptureRef")
        digest = receipt.get("SourceSHA256")
        if not isinstance(ref, str) or not ref.strip():
            raise ValueError("Capture reference required")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("Exact capture SHA256 required")
        observed = _date(receipt.get("ObservedOn"), "ObservedOn")
        if observed > today:
            raise ValueError("Future source observation cannot qualify")
        due_raw = receipt.get("ReviewDueOn")
        due = _date(due_raw, "ReviewDueOn") if due_raw is not None else None
        if due is not None and due < observed:
            raise ValueError("Review date precedes capture observation")
        by_version[key] = receipt
    rows = []
    for key in sorted(mapped_versions):
        source = evidence_versions[key]
        receipt = by_version.get(key)
        if receipt is None:
            state, followup = "unknown", "source-receipt-required"
        elif receipt.get("ReviewDueOn") is None:
            state, followup = "due-date-unset", "source-review-schedule-required"
        elif _date(receipt["ReviewDueOn"], "ReviewDueOn") <= today:
            state, followup = "review-due", "source-review-required"
        else:
            state, followup = "within-review-window", None
        rows.append({
            "EvidenceVersionKey": key,
            "sourceVersion": source["sourceVersion"],
            "ReviewContextKey": context_key,
            "ScopeKey": scope_key,
            "reviewWindow": state,
            "followup": followup,
            "sourceBytesVerified": False,
            "sourceAuthorityVerified": False,
            "implementationObserved": None,
            "accreditationStatus": None,
        })
    return {
        "contractVersion": 1,
        "asOf": today.isoformat(),
        "ReviewContextKey": context_key,
        "ScopeKey": scope_key,
        "graphSha256": validation["graphSha256"],
        "evidence": rows,
        "counts": dict(sorted(Counter(row["reviewWindow"] for row in rows).items())),
        "sourceAuthorityVerified": False,
        "externalAccreditationDecision": None,
        "nativeWrites": 0,
    }
