"""Strict, synthetic-only admission for the offline durable reference ledger.

This is not a credential, an AHPRA transport, a clinical decision or a
production Dataverse boundary. Identity and provider qualification MUST be
supplied by separately authenticated, authorised native source owners.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

from .identity import WatchBinding, reconcile_identity
from .qualification import Qualification, assess_qualified


def _time(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("time not text")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid time") from exc
    if parsed.tzinfo is None:
        raise ValueError("time missing offset")
    return parsed.astimezone(timezone.utc)


def _hold(reason: str, state: str = "unqualified_source") -> dict[str, Any]:
    return {"disposition": state, "human_review_required": True,
            "practice_authorised": False, "reason_codes": [reason]}


@dataclass(frozen=True, slots=True)
class Admission:
    observation: Mapping[str, Any]
    assessment: Mapping[str, Any]
    persistible: bool
    binding_revision: str | None


def _schema_path() -> Path:
    # module/src/registration_assurance/file.py -> CareOps repository root.
    return (Path(__file__).resolve().parents[4]
            / "conductor/tracks/registration_assurance_20261113/registration-observation.schema.json")


def validate_contract(observation: Mapping[str, Any], *, schema_path: Path | None = None) -> None:
    """Enforce full Draft 2020-12/format and extra semantic requirements."""
    if not isinstance(observation, Mapping):
        raise ValueError("observation must be an object")
    path = schema_path if schema_path is not None else _schema_path()
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(dict(observation))
    if observation.get("schemaVersion") != "1.1.0":
        raise ValueError("only lossless 1.1 may enter the reference ledger")
    for field in ("observationId", "watchRef", "idempotencyKey", "correlationId"):
        value = observation.get(field)
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError("empty or noncanonical source identifier")
    if not observation["watchRef"].startswith("test:"):
        raise ValueError("offline reference requires fictional watch namespace")
    practitioner = observation.get("practitioner")
    number = practitioner.get("registrationNumber") if isinstance(practitioner, Mapping) else None
    if (not isinstance(number, str)
            or re.fullmatch(r"(?:TEST|SYNTHETIC)[-_][A-Z0-9-]{3,50}", number) is None):
        raise ValueError("reference store refuses real-looking regulator identifiers")
    evidence = observation.get("evidence")
    if not isinstance(evidence, Mapping) or evidence.get("classification") != "synthetic":
        raise ValueError("reference ledger refuses non-synthetic practitioner evidence")
    if not evidence.get("sourceRef") or not evidence.get("payloadSha256"):
        raise ValueError("evidence requires source reference and digest")
    observed, as_of = _time(observation["observedAtUtc"]), _time(evidence["asOfUtc"])
    if as_of > observed + timedelta(minutes=5):
        raise ValueError("source time cannot postdate observation beyond tolerance")
    if observed.year < 2000:
        raise ValueError("invalid source time")
    # JSON Schema 'format' assertions may be inactive when optional format
    # packages are absent. Enforce calendar validity in the core itself.
    expiry = observation["signal"].get("expiryDate")
    if expiry is not None:
        date.fromisoformat(expiry)
    for restriction in observation["registrationDetail"]["restrictions"]:
        effective = restriction.get("effectiveDate")
        if effective is not None:
            date.fromisoformat(effective)



def admit_observation(
    observation: Mapping[str, Any], *, qualification: Qualification | None,
    bindings: Sequence[WatchBinding], source_profession: str | None,
    purpose: str, now_utc: str, schema_path: Path | None = None,
) -> Admission:
    """Fail closed if identity, schema, trusted purpose or freshness is absent.

    Never infer a match from a name or make a scope-of-practice determination.
    This function does not itself authenticate the trusted input objects.
    """
    if not isinstance(observation, Mapping):
        return Admission({}, _hold("observation_not_object", "invalid_contract"), False, None)
    value = deepcopy(dict(observation))
    try:
        validate_contract(value, schema_path=schema_path)
    except (ValidationError, SchemaError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        # No raw source payload or potentially sensitive error details in result.
        return Admission(value, _hold("observation_schema_or_semantics_invalid", "invalid_contract"), False, None)
    if qualification is None or not qualification.enabled:
        return Admission(value, _hold("no_trusted_provider_qualification"), False, None)
    provider = value["provider"]
    if (not isinstance(purpose, str) or purpose not in qualification.purposes
            or provider["kind"] != qualification.provider_kind
            or provider["qualificationRef"] != qualification.qualification_ref):
        return Admission(value, _hold("provider_contract_or_purpose_mismatch"), False, None)
    permitted = {("AHPRA_PIE_FIND", "qualified_regulatory"),
                 ("AHPRA_PUBLIC_REGISTER_HUMAN", "human_verified")}
    if (provider["kind"], provider["evidenceCeiling"]) not in permitted:
        return Admission(value, _hold("provider_evidence_ceiling_mismatch"), False, None)
    details = value["registrationDetail"]
    if details["sourceVocabularyVersion"] not in qualification.approved_vocabulary:
        return Admission(value, _hold("unknown_regulatory_mapping"), False, None)
    try:
        now = _time(now_utc)
        if not (_time(qualification.effective_from_utc) <= now
                < _time(qualification.effective_to_utc)):
            return Admission(value, _hold("qualification_not_current"), False, None)
        as_of = _time(value["evidence"]["asOfUtc"])
        if now - as_of > timedelta(minutes=qualification.max_source_age_minutes):
            return Admission(value, _hold("source_evidence_too_old", "stale_source"), False, None)
        if as_of > now + timedelta(minutes=5):
            return Admission(value, _hold("source_future_dated", "temporal_conflict"), False, None)
    except (ValueError, TypeError):
        return Admission(value, _hold("qualification_or_source_time_invalid", "temporal_conflict"), False, None)
    if value["sourceHealth"] != "healthy":
        return Admission(value, _hold("source_not_healthy", "source_unavailable"), False, None)
    identity = reconcile_identity(value, bindings, source_profession=source_profession, now_utc=now_utc)
    if identity.status != "matched":
        return Admission(value, _hold(identity.reason, "identity_unresolved"), False, None)

    # The existing source-classifier is the single normalisation authority.
    assessment = assess_qualified(value, qualification=qualification, purpose=purpose, now_utc=now_utc)
    accepted_states = frozenset({
        "source_verified", "verification_required", "restriction_review",
        "expiry_review", "practice_category_review", "potential_adverse_change",
    })
    if assessment.get("practice_authorised") is not False:
        return Admission(value, _hold("classifier_must_not_grant_practice_authority"), False, None)
    return Admission(value, assessment, assessment.get("disposition") in accepted_states,
                     identity.binding_revision)
