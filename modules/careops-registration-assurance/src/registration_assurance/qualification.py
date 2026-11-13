"""Source-qualification gate for synthetic/reference registration observations.

A Qualification is a trusted *input contract*, not a certificate. The real
connector MUST resolve it from protected, authenticated deployment records
and independently prove AHPRA rights and technical source identity.
No transport, secrets, tenant access or authority writes occur here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from .assurance import assess_observation


def _instant(value: str) -> datetime:
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ValueError("invalid ISO timestamp") from exc
    if instant.tzinfo is None:
        raise ValueError("UTC offset required")
    return instant.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class Qualification:
    """Protected, independently checked source entitlement and capability.

    Do not construct from client-provided observation data in production.
    Source contract revision, authentication, rights, retention and DLP remain
    separately required at the provider adapter and native service boundary.
    """

    provider_kind: str
    qualification_ref: str
    purposes: frozenset[str]
    approved_vocabulary: frozenset[str]
    enabled: bool
    effective_from_utc: str
    effective_to_utc: str
    max_source_age_minutes: int

    def __post_init__(self) -> None:
        if not self.provider_kind or not self.provider_kind.strip():
            raise ValueError("provider_kind required")
        if not self.qualification_ref or not self.qualification_ref.strip():
            raise ValueError("qualification_ref required")
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be Boolean")
        if not isinstance(self.purposes, frozenset) or not self.purposes:
            raise ValueError("purposes must be a nonempty frozenset")
        if not isinstance(self.approved_vocabulary, frozenset) or not self.approved_vocabulary:
            raise ValueError("approved_vocabulary must be a nonempty frozenset")
        if any(not isinstance(p, str) or not p.strip() for p in self.purposes | self.approved_vocabulary):
            raise ValueError("approved purposes and vocabularies must be nonempty")
        if type(self.max_source_age_minutes) is not int or self.max_source_age_minutes <= 0:
            raise ValueError("max_source_age_minutes must be a positive integer")
        if _instant(self.effective_from_utc) >= _instant(self.effective_to_utc):
            raise ValueError("qualification effective interval is invalid")


def _held(disposition: str, reason: str) -> dict[str, Any]:
    return {
        "disposition": disposition,
        "human_review_required": True,
        "practice_authorised": False,
        "reason_codes": [reason],
    }


def assess_qualified(
    observation: Mapping[str, Any],
    *,
    qualification: Qualification | None,
    purpose: str,
    now_utc: str,
) -> dict[str, Any]:
    """Enforce a previously authenticated capability before interpreting data.

    A non-null Qualification alone does not prove provider authentication or
    access rights. Clients MUST separately validate the JSON Schema envelope
    and source-backed contract / signed deployment policy. No real-source
    evidence is admitted by this function without that outer boundary.
    """
    if qualification is None or not qualification.enabled:
        return _held("unqualified_source", "missing_or_disabled_qualification")
    if not isinstance(purpose, str) or purpose not in qualification.purposes:
        return _held("unqualified_source", "purpose_not_permitted")
    provider = observation.get("provider")
    if not isinstance(provider, Mapping):
        return _held("unqualified_source", "source_identity_absent")
    if (provider.get("kind") != qualification.provider_kind
            or provider.get("qualificationRef") != qualification.qualification_ref):
        return _held("unqualified_source", "source_qualification_mismatch")
    if observation.get("schemaVersion") not in ("1.0.0", "1.1.0"):
        return _held("unqualified_source", "unsupported_observation_version")
    try:
        current = _instant(now_utc)
    except ValueError:
        return _held("temporal_conflict", "unparseable_evaluation_time")
    if not (_instant(qualification.effective_from_utc) <= current
            < _instant(qualification.effective_to_utc)):
        return _held("unqualified_source", "qualification_outside_effective_period")

    # Provider outages are never current facts, even when an old signal
    # remains present in the source payload.
    health = observation.get("sourceHealth")
    if health != "healthy":
        return _held("source_unavailable", "provider_unavailable_or_stale")

    evidence = observation.get("evidence")
    source_as_of = evidence.get("asOfUtc") if isinstance(evidence, Mapping) else None
    try:
        as_of = _instant(source_as_of)
    except (ValueError, TypeError):
        return _held("temporal_conflict", "source_as_of_not_known")
    if as_of > current + timedelta(minutes=5):
        return _held("temporal_conflict", "future_source_timestamp")
    if current - as_of > timedelta(minutes=qualification.max_source_age_minutes):
        return _held("stale_source", "source_older_than_approved_limit")

    # The 1.0 envelope lacks lossless category/restriction semantics.
    # It may support a review candidate but cannot silently give a positive
    # current-regulator assertion.
    if observation.get("schemaVersion") != "1.1.0":
        return _held("verification_required", "legacy_registration_detail_missing")
    detail = observation.get("registrationDetail")
    if not isinstance(detail, Mapping):
        return _held("verification_required", "regulatory_detail_missing")
    vocabulary = detail.get("sourceVocabularyVersion")
    if vocabulary not in qualification.approved_vocabulary:
        return _held("unqualified_source", "unapproved_status_vocabulary")
    if not detail.get("nativeStatusCode") or not detail.get("categories"):
        return _held("verification_required", "regulator_native_status_missing")

    max_age_hours = (qualification.max_source_age_minutes + 59) // 60
    result = assess_observation(observation, now=now_utc, max_age_hours=max_age_hours)
    # No source assessment is permitted to directly assign employment, local
    # credentialing status or approved clinical SoCP.
    result["practice_authorised"] = False
    return result
