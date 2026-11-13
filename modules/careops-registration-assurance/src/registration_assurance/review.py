"""Pure review-queue reference transitions; never authorises practice or sends alerts.

The caller MUST authenticate reviewer authority and enforce a durable native
compare-and-swap boundary. These functions work only on fictional or separately
approved restricted observations, after source and schema verification.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
from typing import Any, Mapping

_ALLOWED = frozenset({"verified", "rejected", "false_positive", "held", "escalated"})


class ReviewConflict(RuntimeError):
    """A proposed review action is stale or applies to another identity/case."""


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _record(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalise(value: object) -> object:
    if isinstance(value, Mapping):
        return {k: _normalise(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return sorted((_normalise(v) for v in value),
                      key=lambda v: json.dumps(v, sort_keys=True, ensure_ascii=True))
    return value


def _digest(value: object) -> str:
    encoded = json.dumps(_normalise(value), sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("utf-8")
    return sha256(encoded).hexdigest()


def _identity(observation: Mapping[str, Any], assessment: Mapping[str, Any]) -> dict[str, object]:
    watch = _require_text(observation.get("watchRef"), "watchRef")
    practitioner = _record(observation.get("practitioner"))
    return {
        "watchRef": watch,
        "regulator": practitioner.get("regulator"),
        "registrationNumber": practitioner.get("registrationNumber"),
        "reasonCategory": _require_text(assessment.get("disposition"), "disposition"),
    }


def _material(observation: Mapping[str, Any], assessment: Mapping[str, Any]) -> dict[str, object]:
    provider = _record(observation.get("provider"))
    return {
        "identity": _identity(observation, assessment),
        "sourceHealth": observation.get("sourceHealth"),
        "provider": {
            "kind": provider.get("kind"),
            "qualificationRef": provider.get("qualificationRef"),
            "evidenceCeiling": provider.get("evidenceCeiling"),
        },
        "signal": observation.get("signal"),
        "registrationDetail": observation.get("registrationDetail"),
        "reasonCodes": assessment.get("reason_codes"),
    }


def propose_review(previous: Mapping[str, Any] | None, observation: Mapping[str, Any],
                   assessment: Mapping[str, Any]) -> dict[str, Any] | None:
    """Propose review of *material* changes without overwriting human disposition.

    Rechecks with only a new receipt/time are idempotent; the observation store
    separately keeps every permitted source check and its original evidence.
    A change of practitioner identity or review concern needs a distinct case.
    """
    if assessment.get("human_review_required") is not True:
        return deepcopy(dict(previous)) if previous is not None else None

    _require_text(observation.get("observationId"), "observationId")
    identity = _identity(observation, assessment)
    case_id = _digest(["registration-review-v1", identity])
    material_digest = _digest(_material(observation, assessment))

    if previous is not None:
        if previous.get("caseId") != case_id or previous.get("watchRef") != identity["watchRef"]:
            raise ReviewConflict("review case identity changed: create separate case")
        if previous.get("materialDigest") == material_digest:
            return deepcopy(dict(previous))
        version = previous.get("reviewVersion")
        if type(version) is not int or version < 1:
            raise ReviewConflict("invalid existing review version")
        history = deepcopy(previous.get("reviewHistory"))
        if not isinstance(history, list):
            raise ReviewConflict("invalid immutable review history")
        next_version = version + 1
    else:
        history = []
        next_version = 1

    source = _record(observation.get("evidence"))
    return {
        "caseId": case_id,
        "reviewVersion": next_version,
        "reviewState": "pending",
        "watchRef": identity["watchRef"],
        "identity": identity,
        "observationId": observation["observationId"],
        "sourceEvidenceRef": source.get("sourceRef"),
        "materialDigest": material_digest,
        "reasonCategory": identity["reasonCategory"],
        "reasonCodes": sorted(set(assessment.get("reason_codes", []))),
        "reviewHistory": history,
        "practiceAuthorised": False,
    }


def apply_review(case: Mapping[str, Any], disposition: str, *,
                 actor_ref: str, evidence_ref: str, expected_version: int,
                 reviewed_at_utc: str) -> dict[str, Any]:
    """Construct an explicit proposed reviewer disposition, without persistence.

    A native server MUST independently authenticate the actor, permission and
    evidence source and enforce the version before committing this result.
    """
    if type(expected_version) is not int or expected_version < 1:
        raise ReviewConflict("invalid expected review version")
    if case.get("reviewVersion") != expected_version or case.get("reviewState") != "pending":
        raise ReviewConflict("stale or already reviewed case")
    if disposition not in _ALLOWED:
        raise ValueError("unsupported review disposition")
    _require_text(actor_ref, "actor_ref")
    _require_text(evidence_ref, "evidence_ref")
    _require_text(reviewed_at_utc, "reviewed_at_utc")
    try:
        stamp = datetime.fromisoformat(reviewed_at_utc.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("reviewed_at_utc must be a valid offset-aware timestamp") from exc
    if stamp.tzinfo is None:
        raise ValueError("reviewed_at_utc must be offset-aware")
    out = deepcopy(dict(case))
    if out.get("practiceAuthorised") is not False:
        raise ReviewConflict("review record cannot grant practice authority")
    history = out.get("reviewHistory")
    if not isinstance(history, list):
        raise ReviewConflict("review history missing")
    history.append({
        "reviewVersion": expected_version,
        "reviewedAtUtc": reviewed_at_utc,
        "actorRef": actor_ref,
        "evidenceRef": evidence_ref,
        "disposition": disposition,
        "materialDigest": _require_text(case.get("materialDigest"), "materialDigest"),
        "observationId": _require_text(case.get("observationId"), "observationId"),
    })
    out["reviewVersion"] = expected_version + 1
    out["reviewState"] = "reviewed"
    out["practiceAuthorised"] = False
    return out
