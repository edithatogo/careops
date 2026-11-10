"""Tenant-free RIMS publication/person adjudication contract.

Fictional records only. This module validates candidate decision payloads; it does
not authenticate reviewers, write SharePoint, infer employment or send messages.
An authorised native importer must independently verify identity and permissions.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

SCHEMA = "careops-rims.adjudication/1"
PUBLICATION = {"ConfirmedCHHHS", "NotCHHHS", "Uncertain", "Duplicate", "NeedsEvidence"}
EMPLOYMENT = {"EmployeeConfirmed", "NotEmployee", "Uncertain", "HistoricalOrVisiting"}
TYPES = {"publication": PUBLICATION, "employment": EMPLOYMENT}


class AdjudicationError(ValueError):
    """Unsafe or invalid offline decision envelope."""


def fingerprint(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def validate_decision(candidate: dict[str, Any], decision: dict[str, Any], *,
                      expected_candidate_hash: str, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return validated immutable decision copy; refuse stale/unsafe input.

    `previous` is the most recent authorised decision, if one exists.
    This is a *source* contract: reviewer authentication occurs in the tenant.
    """
    if fingerprint(candidate) != expected_candidate_hash:
        raise AdjudicationError("stale or altered candidate")
    required = ("schema", "decision_id", "assertion_type", "subject_id", "status",
                "reviewer_id", "decided_utc", "evidence_hash", "reason",
                "candidate_hash", "supersedes")
    if any(k not in decision for k in required):
        raise AdjudicationError("missing required decision field")
    if decision["schema"] != SCHEMA:
        raise AdjudicationError("unsupported decision schema")
    kind = decision["assertion_type"]
    if not isinstance(kind, str) or kind not in TYPES or decision["status"] not in TYPES[kind]:
        raise AdjudicationError("unknown assertion or status")
    if not all(isinstance(decision[k], str) and decision[k].strip()
               for k in ("decision_id", "subject_id", "reviewer_id", "reason", "evidence_hash", "candidate_hash")):
        raise AdjudicationError("blank identity, provenance or rationale")
    if decision["subject_id"] != candidate.get("subject_id") or kind != candidate.get("assertion_type"):
        raise AdjudicationError("candidate/decision identity mismatch")
    if decision["candidate_hash"] != expected_candidate_hash:
        raise AdjudicationError("candidate hash mismatch")
    if candidate.get("evidence_hash") != decision["evidence_hash"]:
        raise AdjudicationError("evidence changed or not supplied")
    try:
        moment = datetime.fromisoformat(decision["decided_utc"].replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError) as e:
        raise AdjudicationError("invalid decision timestamp") from e
    if moment.tzinfo is None or moment.utcoffset() != timezone.utc.utcoffset(moment):
        raise AdjudicationError("decision timestamp must be UTC")
    if previous:
        if previous.get("decision_id") != decision["supersedes"]:
            raise AdjudicationError("must supersede latest decision")
        if previous.get("subject_id") != decision["subject_id"] or previous.get("assertion_type") != kind:
            raise AdjudicationError("cross-subject supersession")
        if previous.get("decision_id") == decision["decision_id"]:
            raise AdjudicationError("duplicate decision identity")
    elif decision["supersedes"] is not None:
        raise AdjudicationError("unknown prior decision")
    if kind == "employment" and not candidate.get("effective_period"):
        raise AdjudicationError("employment decision requires effective period")
    return dict(decision)


def may_publish(decision: dict[str, Any] | None, *, verify_decision=None) -> bool:
    """Check publication eligibility only after independent decision verification.

    verify_decision must validate the original trusted ledger and reviewer
    authority. It cannot be substituted by a simple Boolean or source claim.
    """
    if not decision or not callable(verify_decision):
        return False
    return bool(decision.get("schema") == SCHEMA
                and decision.get("assertion_type") == "publication"
                and decision.get("status") == "ConfirmedCHHHS"
                and verify_decision(decision))
