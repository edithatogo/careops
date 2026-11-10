"""RIMS offline batch, temporal affiliation and report issue preflight.

No platform calls, writes, emails, employment inference or automatic report
issuance. Verification callbacks MUST be supplied by a trusted native ledger,
not passed through user input. Output is a candidate plan, never an approval.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json


class PreflightError(ValueError):
    """Refuse the entire batch/issuance plan when any condition is unsafe."""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _identity(value, label):
    if not isinstance(value, str) or not value.strip():
        raise PreflightError("missing " + label)
    return value.strip()


def _utc(value):
    try:
        timestamp = datetime.fromisoformat(_identity(value, "UTC timestamp").replace("Z", "+00:00"))
    except ValueError as exc:
        raise PreflightError("invalid UTC timestamp") from exc
    if timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
        raise PreflightError("timestamp must be UTC")
    return timestamp


def _date(value, label):
    try:
        return date.fromisoformat(_identity(value, label))
    except ValueError as exc:
        raise PreflightError("invalid " + label) from exc


def batch_preflight(candidates, latest_decisions, proposals, *, verify_actor=None):
    """All-or-nothing immutable decision plan; never writes to a List.

    verify_actor(proposal, candidate) MUST independently verify authenticated
    reviewer permissions, the source ledger, ETag and review delegation.
    A supplied reviewer_id, signature-like string or bool cannot grant access.
    """
    if not callable(verify_actor):
        raise PreflightError("authoritative reviewer verification unavailable")
    if not all(isinstance(x, list) for x in (candidates, latest_decisions, proposals)):
        raise PreflightError("lists required")
    if not proposals:
        raise PreflightError("empty batch")
    indexed = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise PreflightError("invalid candidate")
        key = (_identity(candidate.get("assertion_type"), "assertion type"),
               _identity(candidate.get("subject_id"), "subject"))
        if key in indexed:
            raise PreflightError("duplicate candidate")
        indexed[key] = candidate
    latest = {}
    for event in latest_decisions:
        if not isinstance(event, dict):
            raise PreflightError("invalid prior decision")
        key = (_identity(event.get("assertion_type"), "prior type"),
               _identity(event.get("subject_id"), "prior subject"))
        if key in latest:
            raise PreflightError("duplicate latest decision")
        latest[key] = event
    allowed = {"publication": {"ConfirmedCHHHS", "NotCHHHS", "Uncertain", "Duplicate", "NeedsEvidence"},
               "employment": {"EmployeeConfirmed", "NotEmployee", "Uncertain", "HistoricalOrVisiting"}}
    seen, ids, prepared = set(), set(), []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            raise PreflightError("invalid proposal")
        kind = _identity(proposal.get("assertion_type"), "type")
        subject = _identity(proposal.get("subject_id"), "subject")
        key = kind, subject
        if key in seen or key not in indexed:
            raise PreflightError("duplicate or missing proposal subject")
        seen.add(key)
        if kind not in allowed or proposal.get("status") not in allowed[kind]:
            raise PreflightError("invalid review disposition")
        decision_id = _identity(proposal.get("decision_id"), "decision ID")
        if decision_id in ids:
            raise PreflightError("duplicate decision ID")
        ids.add(decision_id)
        candidate = indexed[key]
        prior = latest.get(key)
        if proposal.get("candidate_hash") != digest(candidate):
            raise PreflightError("stale candidate hash")
        if proposal.get("evidence_hash") != candidate.get("evidence_hash"):
            raise PreflightError("source evidence mismatch")
        if not _identity(candidate.get("etag"), "List ETag"):
            raise PreflightError("candidate ETag missing")
        if proposal.get("expected_etag") != candidate["etag"]:
            raise PreflightError("stale List ETag")
        if proposal.get("supersedes") != (prior.get("decision_id") if prior else None):
            raise PreflightError("stale decision version")
        _identity(proposal.get("reviewer_id"), "reviewer")
        _identity(proposal.get("reason"), "reason")
        _utc(proposal.get("decided_utc"))
        if kind == "employment":
            span = candidate.get("effective_period")
            if not isinstance(span, dict):
                raise PreflightError("employment period required")
            start = _date(span.get("from"), "employment start")
            if span.get("to") is not None and _date(span["to"], "employment end") < start:
                raise PreflightError("reverse employment period")
        if verify_actor(proposal, candidate) is not True:
            raise PreflightError("actor or source authority not verified")
        prepared.append({"subject_id": subject, "assertion_type": kind, "decision_id": decision_id,
                         "status": proposal["status"], "candidate_hash": proposal["candidate_hash"],
                         "expected_etag": candidate["etag"], "supersedes": proposal.get("supersedes")})
    return {"schema": "careops-rims.batch-preflight/1", "write_authorised": False,
            "count": len(prepared), "candidate_actions": prepared,
            "plan_digest": digest(prepared), "requires_native_revalidation": True}


def temporal_affiliations(person_id, as_of, relationships):
    """Return source-backed, date-effective relationships; never infer employee status."""
    person_id = _identity(person_id, "person")
    instant = _date(as_of, "as-of date")
    result = []
    seen = set()
    allowed = {"Employee", "Visiting", "Collaborator", "Honorary", "Unknown"}
    for row in relationships:
        if row.get("person_id") != person_id:
            continue
        relation_id = _identity(row.get("relationship_id"), "relationship ID")
        if relation_id in seen:
            raise PreflightError("duplicate relationship")
        seen.add(relation_id)
        start = _date(row.get("effective_from"), "effective-from")
        end = _date(row["effective_to"], "effective-to") if row.get("effective_to") else None
        if end and end < start:
            raise PreflightError("reversed affiliation interval")
        if row.get("relationship_kind") not in allowed:
            raise PreflightError("unknown relationship kind")
        if not row.get("evidence_hash"):
            raise PreflightError("relationship evidence required")
        if start <= instant and (end is None or instant <= end):
            result.append({"relationship_id": relation_id,
                           "organisation_id": _identity(row.get("organisation_id"), "organisation"),
                           "relationship_kind": row["relationship_kind"],
                           "evidence_hash": row["evidence_hash"],
                           "employment_confirmed": False})
    return sorted(result, key=lambda x: x["relationship_id"])


def report_issue_preflight(snapshot, decisions, *, verify_decision=None, prior_issue=None):
    """Build a draft change/reissue plan, never an issued document."""
    if not callable(verify_decision):
        raise PreflightError("trusted decision ledger unavailable")
    if not isinstance(snapshot, dict) or not isinstance(decisions, list):
        raise PreflightError("invalid report inputs")
    period = _identity(snapshot.get("period"), "period")
    if len(period) != 7 or period[4] != "-" or not period[:4].isdigit() or not period[5:].isdigit() or not 1 <= int(period[5:]) <= 12:
        raise PreflightError("invalid period")
    source_digest = _identity(snapshot.get("source_digest"), "source digest")
    approved = []
    seen = set()
    for record in decisions:
        subject = _identity(record.get("subject_id"), "publication ID")
        if subject in seen:
            raise PreflightError("duplicate publication")
        seen.add(subject)
        if record.get("assertion_type") != "publication":
            raise PreflightError("employment must not enter publication report")
        if verify_decision(record) is not True:
            raise PreflightError("unverified decision")
        if record.get("status") == "ConfirmedCHHHS":
            approved.append({"subject_id": subject,
                             "decision_id": _identity(record.get("decision_id"), "decision"),
                             "candidate_hash": _identity(record.get("candidate_hash"), "candidate hash")})
    fingerprint = digest({"period": period, "source_digest": source_digest,
                          "approved": sorted(approved, key=lambda v: v["subject_id"])})
    changed = bool(prior_issue and prior_issue.get("snapshot_digest") != fingerprint)
    if prior_issue is not None and prior_issue.get("period") != period:
        raise PreflightError("prior issue period mismatch")
    return {"schema": "careops-rims.report-issue-plan/1", "period": period,
            "snapshot_digest": fingerprint, "approved_count": len(approved),
            "requires_reissue_review": changed, "issue_state": "Draft",
            "publication_authorised": False, "requires_human_issue_approval": True}
