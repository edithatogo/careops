"""Pure bounded check-job state machine. No network, scheduler, store or sends.

Native workers must implement *durable* optimistic concurrency, authenticated
worker identity, source permission, lease acquisition and outbox persistence.
This file provides a deterministic synthetic/reference transition contract.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


class JobConflict(RuntimeError):
    """Rejected stale, conflicting, expired or unauthorised job transition."""


def _utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be text")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be ISO8601") from exc
    if stamp.tzinfo is None:
        raise ValueError("timestamp must include timezone offset")
    return stamp.astimezone(timezone.utc)


def _format(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} required")
    return value


def _version(item: Mapping[str, Any], expected: int) -> None:
    if type(expected) is not int or expected < 1 or item.get("version") != expected:
        raise JobConflict("stale job revision")


def _next(item: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(item))
    if result.get("emailEnabled") is not False:
        raise JobConflict("outbound send must remain disabled")
    if not isinstance(result.get("outbox"), list):
        raise JobConflict("outbox shape invalid")
    result["version"] = item["version"] + 1
    return result


def create_job(*, job_id: str, watch_ref: str, provider_kind: str,
               due_at_utc: str, deadline_utc: str, attempt_limit: int) -> dict[str, Any]:
    """Construct a job object without executing or scheduling anything."""
    _text(job_id, "job_id")
    _text(watch_ref, "watch_ref")
    _text(provider_kind, "provider_kind")
    if type(attempt_limit) is not int or attempt_limit < 1 or attempt_limit > 100:
        raise ValueError("attempt_limit must be an integer in [1, 100]")
    if _utc(deadline_utc) <= _utc(due_at_utc):
        raise ValueError("deadline must follow due time")
    return {
        "jobId": job_id,
        "watchRef": watch_ref,
        "providerKind": provider_kind,
        "state": "queued",
        "attempts": 0,
        "attemptLimit": attempt_limit,
        "version": 1,
        "nextDueUtc": due_at_utc,
        "deadlineUtc": deadline_utc,
        "leaseUntilUtc": None,
        "workerRef": None,
        "outbox": [],
        "emailEnabled": False,
    }


def claim_job(item: Mapping[str, Any], *, worker_ref: str, now_utc: str,
              lease_seconds: int, expected_version: int) -> dict[str, Any]:
    """Claim a queued/due job once for a bounded worker lease."""
    _version(item, expected_version)
    _text(worker_ref, "worker_ref")
    if type(lease_seconds) is not int or lease_seconds < 1 or lease_seconds > 3600:
        raise ValueError("lease_seconds outside 1..3600")
    now = _utc(now_utc)
    if item.get("state") not in ("queued", "retry_due"):
        raise JobConflict("not an eligible queued job")
    if now < _utc(item["nextDueUtc"]) or now >= _utc(item["deadlineUtc"]):
        raise JobConflict("job not due or deadline expired")
    if item.get("attempts", 0) >= item.get("attemptLimit", 0):
        raise JobConflict("retry budget exhausted")
    if now + timedelta(seconds=lease_seconds) > _utc(item["deadlineUtc"]):
        raise JobConflict("lease exceeds deadline")
    result = _next(item)
    result["state"] = "leased"
    result["attempts"] += 1
    result["workerRef"] = worker_ref
    result["leaseUntilUtc"] = _format(now + timedelta(seconds=lease_seconds))
    return result


def complete_job(item: Mapping[str, Any], *, worker_ref: str, now_utc: str,
                 expected_version: int, result_kind: str,
                 observation_id: str | None = None) -> dict[str, Any]:
    """Finish a known worker lease with accepted/held/ambiguous outcome.

    An outbox event is an *internal* pending data event, not a notification or
    permission to send an email or mutate the credentialing master.
    """
    _version(item, expected_version)
    _text(worker_ref, "worker_ref")
    if item.get("state") != "leased" or item.get("workerRef") != worker_ref:
        raise JobConflict("worker does not own the lease")
    now = _utc(now_utc)
    if now > _utc(item["leaseUntilUtc"]) or now >= _utc(item["deadlineUtc"]):
        raise JobConflict("lease or deadline expired; reconcile before retry")
    if result_kind not in ("accepted", "transient_failure", "permanent_failure", "unknown_delivery"):
        raise ValueError("unsupported result_kind")
    if result_kind == "accepted":
        _text(observation_id, "observation_id")

    result = _next(item)
    result["workerRef"] = None
    result["leaseUntilUtc"] = None
    if result_kind == "accepted":
        result["state"] = "succeeded"
        result["outbox"].append({"eventType": "observation_ready", "observationId": observation_id})
    elif result_kind == "unknown_delivery":
        result["state"] = "needs_reconciliation"
    elif result_kind == "permanent_failure":
        result["state"] = "blocked"
    else:
        delay = min(60 * (2 ** (result["attempts"] - 1)), 3600)
        due = now + timedelta(seconds=delay)
        if result["attempts"] >= result["attemptLimit"] or due >= _utc(result["deadlineUtc"]):
            result["state"] = "dead_letter"
        else:
            result["state"] = "retry_due"
            result["nextDueUtc"] = _format(due)
    return result


def recover_expired_lease(item: Mapping[str, Any], *, now_utc: str,
                          expected_version: int) -> dict[str, Any]:
    """Quarantine an expired lease until durable readback resolves uncertainty."""
    _version(item, expected_version)
    if item.get("state") != "leased":
        raise JobConflict("job has no active lease")
    if _utc(now_utc) <= _utc(item["leaseUntilUtc"]):
        raise JobConflict("lease has not expired")
    result = _next(item)
    result["state"] = "needs_reconciliation"
    result["workerRef"] = None
    result["leaseUntilUtc"] = None
    return result
