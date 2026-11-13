"""Pure, provider-neutral semantic checks for the proposed CareOps MJP v1 wire contract.

This is a source-level companion to JSON Schema, not an authentication, native
SharePoint, industrial-policy or business approval engine. A caller MUST
validate the envelope with Draft202012Validator + FormatChecker first.
"""
from __future__ import annotations

from datetime import datetime, timezone

_PURPOSE = {
    "policy.reference": "policy-reconciliation",
    "approval.request": "workflow-decision",
    "approval.result": "workflow-decision",
    "lifecycle.event": "process-intelligence",
    "workforce.aggregate": "workforce-analytics",
    "costing.aggregate": "cost-evaluation",
    "simulation.scenario": "scenario-modelling",
    "source.reference": "source-qualification",
}
_ROUTE = {
    "policy.reference": ("careops-ppg", "careops-medical-job-planning"),
    "approval.request": ("careops-medical-job-planning", "careops-approve"),
    "approval.result": (("careops-approve", "careops-decisions"), "careops-medical-job-planning"),
    "lifecycle.event": ("careops-medical-job-planning", "careops-process"),
    "workforce.aggregate": ("careops-medical-job-planning", "careops-workforce"),
    "costing.aggregate": ("careops-medical-job-planning", ("careops-costing", "careops-finance")),
    "simulation.scenario": ("careops-medical-job-planning", "careops-sim"),
    "source.reference": (None, "careops-medical-job-planning"),
}


def _utc_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be RFC3339 UTC text")
    value = value.replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be explicitly UTC")
    return timestamp.astimezone(timezone.utc)


def semantic_errors(message: dict) -> list[str]:
    """Return violations after structural validation.

    This never grants authority. Identity, delegation, confidentiality, and
    source completeness MUST be confirmed by the actual operational provider.
    """
    errors: list[str] = []
    kind = message.get("message_type")
    payload = message.get("payload", {})
    quality = message.get("quality", {})
    if not isinstance(payload, dict) or not isinstance(quality, dict):
        return ["payload/quality must be objects"]

    if message.get("purpose") != _PURPOSE.get(kind):
        errors.append("purpose disagrees with message type")
    route = _ROUTE.get(kind)
    if route:
        sender, receiver = route
        producer = message.get("producer", {}).get("module")
        consumer = message.get("consumer", {}).get("module")
        if sender is not None and producer not in (sender if isinstance(sender, tuple) else (sender,)):
            errors.append("producer module disagrees with interface authority")
        if consumer not in (receiver if isinstance(receiver, tuple) else (receiver,)):
            errors.append("consumer module disagrees with interface authority")

    try:
        observed = _utc_time(message["observed_at"])
        quality_as_of = _utc_time(quality["as_of"])
        if quality_as_of > observed:
            errors.append("quality as_of occurs after observation")
        if "as_of" in message and _utc_time(message["as_of"]) > observed:
            errors.append("report as_of occurs after observation")
        if "effective_from" in message and "effective_to" in message:
            if _utc_time(message["effective_to"]) < _utc_time(message["effective_from"]):
                errors.append("inverted effective interval")
    except (ValueError, TypeError, KeyError, OverflowError):
        errors.append("invalid or non-UTC temporal metadata")

    counts = ("eligible_count", "observed_count", "missing_count")
    present = [key in quality for key in counts]
    if any(present) and not all(present):
        errors.append("quality population counts must be supplied together")
    if all(present):
        eligible, observed_count, missing = (quality[key] for key in counts)
        if any(type(n) is not int or n < 0 for n in (eligible, observed_count, missing)):
            errors.append("quality counts must be nonnegative integers")
        elif observed_count + missing != eligible:
            errors.append("quality eligible must equal observed plus missing")
        if quality.get("status") == "complete" and missing != 0:
            errors.append("complete quality cannot have missing source records")
        if quality.get("status") == "unavailable" and observed_count > 0:
            errors.append("unavailable source cannot have observed records")

    if kind in ("workforce.aggregate", "costing.aggregate"):
        if payload.get("service_key") != message.get("context", {}).get("scope_key"):
            errors.append("aggregate service does not match scoped request")
        if payload.get("period_start", "") > payload.get("period_end", ""):
            errors.append("inverted aggregate period")

    if kind == "workforce.aggregate":
        if not all(present):
            errors.append("workforce aggregate requires complete coverage counts")
        else:
            if payload.get("missing_count") != quality.get("missing_count"):
                errors.append("payload and envelope missing populations disagree")
            if payload.get("eligible_population") != quality.get("eligible_count"):
                errors.append("payload and envelope eligible populations disagree")
            if quality.get("missing_count", 0) > 0 and quality.get("status") == "complete":
                errors.append("missing workforce observations cannot be complete")
        if payload.get("suppression_status") != quality.get("suppression"):
            errors.append("payload and envelope suppression disagree")
        if quality.get("suppression") in {"applied", "withheld"}:
            if any(payload.get(key) is not None for key in
                   ("numerator", "denominator", "value", "eligible_population")):
                errors.append("suppressed numeric aggregate must contain nulls")

    if kind == "approval.result":
        if payload.get("outcome") == "conditional_approval" and not payload.get("conditions_evidence_ref"):
            errors.append("conditional approval requires evidence reference")
        try:
            if _utc_time(payload["decided_at"]) > _utc_time(message["observed_at"]):
                errors.append("decision occurred after observed message")
        except (ValueError, TypeError, KeyError, OverflowError):
            errors.append("invalid decision timestamp")

    if kind == "source.reference" and payload.get("verification_status") != "verified":
        if quality.get("status") == "complete":
            errors.append("unverified source reference cannot claim complete coverage")

    return errors
