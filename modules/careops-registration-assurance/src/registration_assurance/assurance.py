"""Pure fail-closed registration-assurance rules. No tenant, API or authority writes."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence
import json

_UNAVAILABLE = frozenset({"blocked", "rate_limited", "transport_error", "schema_drift", "stale", "unknown"})
_ADVERSE = frozenset({"not_registered", "suspended", "cancelled"})
_ALLOWED_QUALIFIED = frozenset({"AHPRA_PIE_FIND", "AHPRA_PUBLIC_REGISTER_HUMAN"})
_SOURCE_LIMITS = {
    "MOCK": "test_only",
    "AHPRA_PUBLIC_AUTOCOMPLETE": "discovery_only",
    "AHPRA_PIE_FIND": "qualified_regulatory",
    "AHPRA_PIE_IDENTITY": "qualified_identity_only",
    "AHPRA_PUBLIC_REGISTER_HUMAN": "human_verified",
}


def _value(obj: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    found = obj.get(field)
    return found if isinstance(found, dict) else {}


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if result.tzinfo is None:
        return None
    return result.astimezone(timezone.utc)


def _decision(disposition: str, *, review: bool, reasons: Sequence[str]) -> dict[str, Any]:
    return {"disposition": disposition, "human_review_required": review,
            "practice_authorised": False, "reason_codes": list(reasons)}


def assess_observation(observation: Mapping[str, Any], *, now: str | None = None,
                       max_age_hours: int = 48) -> dict[str, Any]:
    """Assess source evidence, never entitlement to practise.

    Validate the full versioned JSON Schema at the provider boundary first.
    This reference engine is a second, independent semantic guard only.
    """
    if max_age_hours <= 0:
        raise ValueError("max_age_hours must be positive")
    provider = _value(observation, "provider")
    signal = _value(observation, "signal")
    practitioner = _value(observation, "practitioner")
    evidence = _value(observation, "evidence")
    details = _value(observation, "registrationDetail")

    kind, ceiling = provider.get("kind"), provider.get("evidenceCeiling")
    if kind not in _SOURCE_LIMITS:
        return _decision("unqualified_source", review=True, reasons=["unknown_provider"])
    if kind == "MOCK":
        return _decision("synthetic_only", review=False, reasons=["test_data_not_operational"])
    if kind == "AHPRA_PUBLIC_AUTOCOMPLETE":
        return _decision("discovery_only", review=False, reasons=["name_suggestion_is_not_registration"])
    if ceiling != _SOURCE_LIMITS[kind] or not provider.get("qualificationRef"):
        return _decision("unqualified_source", review=True, reasons=["provider_ceiling_or_agreement_invalid"])
    if kind == "AHPRA_PIE_IDENTITY":
        return _decision("identity_evidence_only", review=True, reasons=["identity_service_not_status_provider"])
    if kind not in _ALLOWED_QUALIFIED:
        return _decision("unqualified_source", review=True, reasons=["provider_not_admitted"])
    if observation.get("sourceHealth") in _UNAVAILABLE or observation.get("sourceHealth") != "healthy":
        return _decision("source_unavailable", review=True, reasons=["source_not_currently_available"])
    if (practitioner.get("regulator") != "AHPRA"
            or not isinstance(practitioner.get("registrationNumber"), str)
            or not practitioner.get("registrationNumber", "").strip()
            or signal.get("identityState") != "matched"):
        return _decision("identity_unresolved", review=True, reasons=["exact_registration_identity_not_confirmed"])
    if not evidence.get("sourceRef"):
        return _decision("evidence_missing", review=True, reasons=["missing_source_reference"])
    observed = _parse_time(observation.get("observedAtUtc"))
    as_of = _parse_time(evidence.get("asOfUtc"))
    current = observed if now is None else _parse_time(now)
    if observed is None or current is None or as_of is None:
        return _decision("temporal_conflict", review=True, reasons=["time_missing_or_invalid"])
    if as_of > observed + timedelta(minutes=5) or as_of > current + timedelta(minutes=5):
        return _decision("temporal_conflict", review=True, reasons=["source_as_of_in_future"])
    if current - as_of > timedelta(hours=max_age_hours):
        return _decision("stale_source", review=True, reasons=["source_evidence_too_old"])
    status = signal.get("registrationStatus")
    if status not in {"registered", *_ADVERSE}:
        return _decision("verification_required", review=True, reasons=["unknown_or_unmapped_status"])
    if status in _ADVERSE:
        return _decision("potential_adverse_change", review=True, reasons=["verified_adverse"])
    native_status = details.get("nativeStatusCode")
    vocabulary = details.get("sourceVocabularyVersion")
    categories = details.get("categories")
    if (not isinstance(native_status, str) or not native_status
            or not isinstance(vocabulary, str) or not vocabulary
            or not isinstance(categories, list) or not categories):
        return _decision("verification_required", review=True, reasons=["registration_category_or_native_code_missing"])
    if "non_practising" in categories:
        return _decision("practice_category_review", review=True, reasons=["non_practising_registration"])
    if details.get("restrictions") or signal.get("conditionsIndicator") == "present":
        return _decision("restriction_review", review=True, reasons=["conditions_or_undertakings_require_review"])
    if signal.get("conditionsIndicator") != "absent":
        return _decision("verification_required", review=True, reasons=["restriction_status_unknown"])
    expiry_date = signal.get("expiryDate")
    if isinstance(expiry_date, str):
        try:
            if datetime.fromisoformat(expiry_date).date() < current.date():
                return _decision("expiry_review", review=True, reasons=["expiry_needs_regulator_interpretation"])
        except ValueError:
            return _decision("verification_required", review=True, reasons=["invalid_expiry_date"])
    return _decision("source_verified", review=False, reasons=["qualified_source_observation_only"])


def _same_content(item: Mapping[str, Any]) -> str:
    normalized = {k: item.get(k) for k in ("watchRef", "practitioner", "provider", "sourceHealth", "signal", "registrationDetail")}
    normalized["asOfUtc"] = _value(item, "evidence").get("asOfUtc")
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def reconcile_observations(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Pure replay reference model; a newer native register decision is never changed.

    This is NOT a durable store. Native adapters must implement concurrency and
    persistence while preserving all raw and superseded evidence privately.
    """
    accepted: list[str] = []
    duplicates: list[str] = []
    conflicts: list[str] = []
    superseded: list[str] = []
    seen: set[str] = set()
    current: Mapping[str, Any] | None = None
    for item in items:
        item_id = str(item.get("observationId", ""))
        semantic = _same_content(item)
        if semantic in seen:
            duplicates.append(item_id)
            continue
        seen.add(semantic)
        stamp = _parse_time(_value(item, "evidence").get("asOfUtc"))
        if stamp is None:
            conflicts.append(item_id)
            continue
        if current is None:
            accepted.append(item_id)
            current = item
            continue
        prev = _parse_time(_value(current, "evidence").get("asOfUtc"))
        if prev is None or stamp == prev:
            conflicts.append(item_id)
        elif stamp < prev:
            superseded.append(item_id)
        else:
            accepted.append(item_id)
            current = item
    return {"accepted": accepted, "duplicates": duplicates, "conflicts": conflicts,
            "superseded": superseded,
            "currentObservationId": current.get("observationId") if current else None}


def assess_engagement_coverage(engagements: Sequence[Mapping[str, Any]],
                               watchlist: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Compute *monitor coverage* for authorised engagements, not practice rights.

    Caller handles eligibility, source freshness, identity mapping and access.
    The pseudonymous refs returned here belong only in a restricted review queue.
    """
    by_watch: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for w in watchlist:
        by_watch[str(w.get("watchRef", ""))].append(w)
    by_facility: dict[str, dict[str, int]] = defaultdict(lambda: {"eligible": 0, "covered": 0})
    by_kind: dict[str, dict[str, int]] = defaultdict(lambda: {"eligible": 0, "covered": 0})
    covered = 0
    unmatched: list[str] = []
    ambiguous: list[str] = []
    counted: set[str] = set()
    for e in engagements:
        if e.get("active") is not True:
            continue
        engagement_ref = str(e.get("engagementRef", ""))
        if not engagement_ref or engagement_ref in counted:
            if engagement_ref:
                ambiguous.append(engagement_ref)
            continue
        counted.add(engagement_ref)
        facility = str(e.get("facilityRef") or "unmapped")
        kind = str(e.get("kind") or "unmapped")
        by_facility[facility]["eligible"] += 1
        by_kind[kind]["eligible"] += 1
        records = by_watch.get(str(e.get("watchRef", "")), [])
        if len(records) > 1:
            ambiguous.append(engagement_ref)
        elif (len(records) == 1 and records[0].get("enabled") is True
              and isinstance(records[0].get("registrationNumber"), str)
              and records[0]["registrationNumber"].strip()):
            covered += 1
            by_facility[facility]["covered"] += 1
            by_kind[kind]["covered"] += 1
        else:
            unmatched.append(engagement_ref)
    return {"eligible": len(counted), "covered": covered, "unmatched": unmatched,
            "ambiguous": ambiguous, "byFacility": dict(by_facility), "byKind": dict(by_kind),
            "coverageFraction": (covered / len(counted)) if counted else None}
