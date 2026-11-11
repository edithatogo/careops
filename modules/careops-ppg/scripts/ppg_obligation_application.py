# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Read-only publisher force and local document-adoption overlay for PPG accreditation.

This is an overlay over the *existing* versioned accreditation graph, not a new
requirements register, legal interpretation, policy approval or accreditor. A
source link or locally adopted document never establishes implementation.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from scripts.ppg_accreditation_contract import validate_graph

SOURCE_KINDS = frozenset({
    "internal-ppg", "external-directive", "external-guideline",
    "external-standard", "college-accreditation", "legislation",
})
FORCES = {
    "internal-ppg": {"unverified", "locally-approved"},
    "external-directive": {"unverified", "publisher-mandated"},
    "external-guideline": {"unverified", "guidance"},
    "external-standard": {"unverified", "scheme-requirement", "guidance"},
    "college-accreditation": {"unverified", "scheme-requirement"},
    "legislation": {"unverified", "publisher-mandated"},
}
STATES = frozenset({"proposed", "adopted", "not-adopted", "withdrawn"})


def _required(row: dict, *fields: str) -> None:
    if not isinstance(row, dict) or any(
        not isinstance(row.get(f), str) or not row[f].strip() for f in fields
    ):
        raise ValueError("Missing source identity or human decision field")


def _date(value: Any, name: str) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("Invalid " + name)
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid " + name) from exc
    if parsed.isoformat() != value:
        raise ValueError("Invalid " + name)
    return parsed


def _interval_overlap(a: dict, b: dict) -> bool:
    first = max(_date(a["EffectiveFrom"], "EffectiveFrom"),
                _date(b["EffectiveFrom"], "EffectiveFrom"))
    upper = []
    for row in (a, b):
        if row.get("EffectiveTo") is not None:
            upper.append(_date(row["EffectiveTo"], "EffectiveTo"))
    return not upper or first <= min(upper)


def project_obligations(graph: dict, profiles: list[dict],
                        adoptions: list[dict], context_key: str,
                        scope_key: str, *, as_of: str) -> dict:
    """Produce a deterministic version/scope-bound queue without judgement.

    Profiles must be tied to a capture from their *same framework*; a human
    decision classifies force as a candidate review only, not proof of legal
    applicability. Adopted documents are linked by existing evidence-version
    keys and their existing requirement mappings.
    """
    validation = validate_graph(graph)
    today = _date(as_of, "as_of")
    if (not isinstance(profiles, list) or not isinstance(adoptions, list)
            or any(not isinstance(x, dict) for x in profiles + adoptions)):
        raise ValueError("Profiles and adoptions must be arrays of objects")
    contexts = {row["ReviewContextKey"]: row for row in graph["contexts"]}
    context = contexts.get(context_key)
    if context is None or scope_key not in context["ScopeKeys"]:
        raise ValueError("Review context scope mismatch")
    requirements = {row["RequirementKey"]: row for row in graph["requirements"]}
    versions = {row["EvidenceVersionKey"]: row for row in graph["evidenceVersions"]}
    mapping_by_requirement: dict[str, set[str]] = {}
    for mapping in graph["mappings"]:
        if (mapping["ReviewContextKey"] == context_key
                and mapping["ScopeKey"] == scope_key):
            mapping_by_requirement.setdefault(mapping["RequirementKey"], set()).add(
                mapping["EvidenceVersionKey"])

    indexed_profiles: dict[str, dict] = {}
    for profile in profiles:
        _required(profile, "FrameworkKey", "SourceKind", "NormativeForce",
                  "PublisherRef", "CaptureKey")
        key = profile["FrameworkKey"]
        if key in indexed_profiles or key not in context["FrameworkKeys"]:
            raise ValueError("Duplicate or out-of-context framework profile")
        kind, force = profile["SourceKind"], profile["NormativeForce"]
        if kind not in SOURCE_KINDS or force not in FORCES[kind]:
            raise ValueError("Source kind and normative force incompatible")
        if not any(r["FrameworkKey"] == key
                   and r["source"]["CaptureKey"] == profile["CaptureKey"]
                   for r in requirements.values()):
            raise ValueError("Framework source capture unverified")
        review = profile.get("ForceReview")
        if force != "unverified":
            if not isinstance(review, dict):
                raise ValueError("Reviewed force requires force review")
            _required(review, "ActorRef", "DecisionRef", "SourceLocator", "ReviewedAt")
            if _date(review["ReviewedAt"], "ReviewedAt") > today:
                raise ValueError("Source force review is in the future")
        elif review is not None:
            raise ValueError("Unverified source force must not claim force review")
        indexed_profiles[key] = profile

    scope_versions: dict[str, list[dict]] = {}
    seen_keys: set[str] = set()
    for adoption in adoptions:
        _required(adoption, "AdoptionKey", "EvidenceVersionKey",
                  "ScopeKey", "State", "EffectiveFrom")
        key, version_key = adoption["AdoptionKey"], adoption["EvidenceVersionKey"]
        if key in seen_keys:
            raise ValueError("Duplicate adoption identity")
        seen_keys.add(key)
        if version_key not in versions:
            raise ValueError("Unknown evidence version")
        if adoption["ScopeKey"] != scope_key:
            raise ValueError("Adoption outside review context scope")
        state = adoption["State"]
        if state not in STATES:
            raise ValueError("Unsupported local adoption state")
        start = _date(adoption["EffectiveFrom"], "EffectiveFrom")
        end = (None if adoption.get("EffectiveTo") is None
               else _date(adoption["EffectiveTo"], "EffectiveTo"))
        if end is not None and end < start:
            raise ValueError("Adoption effective interval invalid")
        if state in {"adopted", "withdrawn", "not-adopted"}:
            _required(adoption, "DecisionRef", "ActorRef", "DecidedAt")
            if _date(adoption["DecidedAt"], "DecidedAt") > today:
                raise ValueError("Human adoption decision is in the future")
        elif any(adoption.get(x) is not None
                 for x in ("DecisionRef", "ActorRef", "DecidedAt")):
            raise ValueError("Proposed adoption cannot claim a decision")
        evidence_key = versions[version_key]["EvidenceKey"]
        scope_versions.setdefault(evidence_key, []).append(adoption)

    for items in scope_versions.values():
        adopted = [row for row in items if row["State"] == "adopted"]
        for index, first in enumerate(adopted):
            for second in adopted[index + 1:]:
                if _interval_overlap(first, second):
                    raise ValueError("conflicting adoption versions for one evidence identity")

    out = []
    for requirement in sorted(graph["requirements"], key=lambda r:
                              (r["FrameworkKey"], r["RequirementKey"])):
        if requirement["FrameworkKey"] not in context["FrameworkKeys"]:
            continue
        profile = indexed_profiles.get(requirement["FrameworkKey"])
        keys = mapping_by_requirement.get(requirement["RequirementKey"], set())
        related = [a for a in adoptions if a["EvidenceVersionKey"] in keys]
        statuses = []
        for adoption in related:
            state = adoption["State"]
            if state != "adopted":
                statuses.append(state)
                continue
            if today < _date(adoption["EffectiveFrom"], "EffectiveFrom"):
                statuses.append("scheduled")
            elif adoption.get("EffectiveTo") is not None and today > _date(
                    adoption["EffectiveTo"], "EffectiveTo"):
                statuses.append("expired")
            else:
                statuses.append("adopted")
        if "adopted" in statuses:
            selected = "adopted"
        elif "scheduled" in statuses:
            selected = "scheduled"
        elif "expired" in statuses:
            selected = "expired"
        elif "withdrawn" in statuses:
            selected = "withdrawn"
        elif "not-adopted" in statuses:
            selected = "not-adopted"
        elif "proposed" in statuses:
            selected = "proposed"
        else:
            selected = "unobserved"
        matches = [a for a in graph["assessments"]
                   if a["RequirementKey"] == requirement["RequirementKey"]
                   and a["ScopeKey"] == scope_key
                   and a["ReviewContextKey"] == context_key]
        if len(matches) > 1:
            raise ValueError("Duplicate scoped assessment")
        out.append({
            "RequirementKey": requirement["RequirementKey"],
            "FrameworkKey": requirement["FrameworkKey"],
            "ScopeKey": scope_key,
            "sourceKind": profile["SourceKind"] if profile else "unclassified",
            "normativeForce": profile["NormativeForce"] if profile else "unverified",
            "sourceAuthorityVerified": False,
            "localAdoption": selected,
            "adoptionKeys": sorted(a["AdoptionKey"] for a in related),
            "applicability": matches[0]["applicability"] if matches else "unknown",
            "implementationObserved": None,
            "complianceRating": None,
        })
    return {
        "contractVersion": 1, "graphSha256": validation["graphSha256"],
        "asOf": today.isoformat(), "ReviewContextKey": context_key,
        "ScopeKey": scope_key, "requirements": out,
        "countsByLocalAdoption": dict(sorted(Counter(
            row["localAdoption"] for row in out).items())),
        "forceClassificationIsHumanCandidate": True,
        "sourceAuthorityVerified": False, "acceptanceTransferred": False,
        "externalAccreditationDecision": None, "nativeWrites": 0,
    }
