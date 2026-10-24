"""Render the fixed fictional F10 scenario result as a diagnostic test report.

This is not an action worklist. It has no file, network, provider or persistence
capability; callers receive a string and decide how to inspect it locally.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
import re


_TOP_LEVEL_KEYS = {
    "status", "claims_status", "meeting", "source", "all_cases",
    "proposed_review", "excluded_review", "blocking_exceptions",
    "chair_selection_required", "agenda_updated", "register_updated",
    "planner_updated", "notified",
}
_ROW_KEYS = {
    "case_id", "lane", "reasons", "source_snapshot", "claims_status",
    "selected_for_agenda", "issued", "assigned", "notified", "committed", "closed",
}
_SOURCE_KEYS = {
    "case_id", "source_id", "snapshot_version", "reviewed_version", "snapshot_time",
    "record_id", "source_text", "status", "commissioned_claim", "issued_claim",
    "owner_claim", "review_date", "due_date", "closure_acceptance", "closure_evidence_ref",
    "meeting_confirmed_claim", "duplicate_claim", "conflict_claim", "history", "response_ref",
}
_LANES = {
    "PROPOSED_REVIEW": "Proposed for human review; not selected",
    "EXCLUDED_REVIEW": "Excluded from the proposed review",
    "BLOCKING_EXCEPTION": "Blocked for manual reconciliation",
}
_ROW_EFFECTS = ("selected_for_agenda", "issued", "assigned", "notified", "committed", "closed")
_TOP_EFFECTS = ("agenda_updated", "register_updated", "planner_updated", "notified")
_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
_REASONS = re.compile(r"^(?:[A-Z][A-Z0-9_]*;)*$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$")
_F10_REV4_OUTPUT_SHA256 = "7bbec49bad7bd8e3e4ad0736a8fe749c13cff3e019dd97f26dd7659b182a44ad"
_STATUS_LABELS = {
    "open": "Open (supplied)",
    "held": "Held (supplied)",
    "closed": "Closed (supplied)",
    "closure_pending": "Closure pending (supplied)",
    "awaiting_response": "Awaiting response (supplied)",
    "no_follow_up": "No follow-up (supplied)",
    "superseded": "Superseded (supplied)",
}
_REASON_LABELS = {
    "ACCEPTED_CLOSED": "supplied closure status is accepted closed",
    "CLOSURE_ACCEPTANCE_CONFLICT": "closure-pending status conflicts with a supplied acceptance claim",
    "CLOSURE_PENDING": "reported complete but closure acceptance remains pending",
    "DATE_NOT_EVIDENCED": "no due date or review date was supplied",
    "DUPLICATE_OR_CONFLICT": "a duplicate or conflicting-record claim was supplied",
    "HELD": "the supplied status is held",
    "MEETING_UNCONFIRMED": "the meeting confirmation claim is missing or false",
    "NOT_ISSUED": "the item is not claimed as issued",
    "NO_FOLLOW_UP": "the supplied decision says no follow-up is needed",
    "OWNER_NOT_EVIDENCED": "no accountable owner claim was supplied",
    "RESPONSE_UNANSWERED": "a response is still reported as unanswered",
    "STALE_SNAPSHOT": "snapshot and reviewed versions differ",
    "UNCOMMISSIONED": "the item is not claimed as commissioned",
    "UNKNOWN_STATUS": "the supplied status is outside the recognized set",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _check_token(value: object, label: str) -> str:
    _require(isinstance(value, str) and bool(_TOKEN.fullmatch(value)), f"Invalid {label}.")
    return value


def _validate_case(row: object) -> dict:
    _require(isinstance(row, dict) and set(row) == _ROW_KEYS, "F10 scenario row has an unexpected shape.")
    case_id = _check_token(row["case_id"], "scenario case ID")
    _require(isinstance(row["lane"], str) and row["lane"] in _LANES,
             f"Unknown review lane in {case_id}.")
    _require(isinstance(row["reasons"], str) and bool(_REASONS.fullmatch(row["reasons"])),
             f"Invalid reason codes in {case_id}.")
    _require(row["claims_status"] == "UNVERIFIED_FICTIONAL_INPUT", f"Unverified status missing in {case_id}.")
    _require(all(row[key] is False for key in _ROW_EFFECTS), f"Effect flag is true in {case_id}.")

    source = row["source_snapshot"]
    _require(isinstance(source, dict) and set(source) == _SOURCE_KEYS,
             f"Source snapshot has an unexpected shape in {case_id}.")
    _require(source["case_id"] == case_id, f"Scenario ID mismatch in {case_id}.")
    source_id = _check_token(source["source_id"], f"source ID in {case_id}")
    record_id = _check_token(source["record_id"], f"record ID in {case_id}")
    _require(source_id.startswith("FICTIONAL-") and record_id.startswith("FICTIONAL-"),
             f"Non-fictional source or record ID in {case_id}.")
    for key in ("snapshot_version", "reviewed_version"):
        _check_token(source[key], f"{key} in {case_id}")
    snapshot_time = source["snapshot_time"]
    _require(isinstance(snapshot_time, str) and bool(_TIMESTAMP.fullmatch(snapshot_time)),
             f"Invalid canonical snapshot time in {case_id}.")
    try:
        parsed_time = datetime.fromisoformat(snapshot_time)
    except ValueError as error:
        raise ValueError(f"Invalid snapshot time in {case_id}.") from error
    _require(parsed_time.tzinfo is not None and parsed_time.utcoffset() is not None,
             f"Snapshot time lacks a timezone in {case_id}.")
    status = source["status"]
    _require(isinstance(status, str) and bool(_TOKEN.fullmatch(status)), f"Invalid supplied status in {case_id}.")
    return row


def _render_f10_test_catalog(result: object) -> str:
    """Return an in-memory report for the F10 rev4 fictional test catalog.

    Repeated source-record IDs are allowed because the native cases are
    alternative scenarios. The report labels them as such and never calls them
    a coherent snapshot, action list, agenda, or register.
    """
    _require(isinstance(result, dict) and set(result) == _TOP_LEVEL_KEYS,
             "F10 result has an unexpected top-level shape.")
    _require(result["status"] == "PROPOSAL_ONLY", "F10 result is not proposal-only.")
    _require(result["claims_status"] == "UNVERIFIED_FICTIONAL_INPUT",
             "F10 result does not identify unverified fictional input.")
    _require(result["meeting"] == "fictional occurrence; no actual meeting identity verified",
             "F10 meeting identity is not the pinned fictional label.")
    _require(result["source"] == "fixed fictional snapshot; no live register read",
             "F10 source is not the pinned fictional snapshot.")
    _require(result["chair_selection_required"] is True, "Human selection requirement is missing.")
    _require(all(result[key] is False for key in _TOP_EFFECTS), "Top-level external-effect flag is true.")
    cases = result["all_cases"]
    _require(isinstance(cases, list) and bool(cases), "F10 result has no scenario rows.")
    validated = [_validate_case(row) for row in cases]
    case_ids = [row["case_id"] for row in validated]
    _require(len(case_ids) == len(set(case_ids)), "Scenario case IDs must be unique.")

    by_lane: dict[str, list[dict]] = {lane: [] for lane in _LANES}
    for row in validated:
        by_lane[row["lane"]].append(row)
    group_keys = {
        "PROPOSED_REVIEW": "proposed_review",
        "EXCLUDED_REVIEW": "excluded_review",
        "BLOCKING_EXCEPTION": "blocking_exceptions",
    }
    for lane, key in group_keys.items():
        grouped = result[key]
        _require(isinstance(grouped, list) and all(isinstance(item, dict) for item in grouped),
                 f"F10 {key} lane is malformed.")
        _require(grouped == by_lane[lane], f"F10 {key} does not match the full scenario rows.")

    record_counts = Counter(row["source_snapshot"]["record_id"] for row in validated)
    repeated = sorted(record_id for record_id, count in record_counts.items() if count > 1)
    lines = [
        "# FICTIONAL TEST CATALOG - NOT A WORKLIST / NOT FOR ACTION",
        "",
        "**Result:** PROPOSAL ONLY. Supplied claims are UNVERIFIED_FICTIONAL_INPUT.",
        "**Meeting:** fictional occurrence; no actual meeting identity verified.",
        "**Source:** fixed fictional snapshot; no live register read.",
        "**Current action status:** not applicable; no scenario is a current or accepted action.",
        f"**Coverage:** {len(validated)} alternative test scenarios; " + "; ".join(
            f"{len(by_lane[lane])} {label.lower()}" for lane, label in _LANES.items()
        ) + ".",
        "**Meaning:** scenario rows test different cases. They are not simultaneous actions or one coherent snapshot.",
        "**Repeated fictional record IDs:** " + (", ".join(repeated) if repeated else "none") + ".",
        "**Effects:** no agenda, register, or Planner update; no notification. Each scenario has selection, issue, assignment, notification, commit, and closure flags set to false. Human selection is required.",
        "**Real carry-forward:** use the existing manual source-linked review. This report does not select, issue, assign, close, or track work.",
        "",
    ]
    for row in validated:
        source = row["source_snapshot"]
        version = f"{source['snapshot_version']} / {source['reviewed_version']}"
        if source["snapshot_version"] != source["reviewed_version"]:
            version += " (mismatch)"
        status = _STATUS_LABELS.get(source["status"], f"Unrecognized supplied state: {source['status']}")
        reason_codes = [code for code in row["reasons"].split(";") if code]
        reasons = "; ".join(
            f"{code}: {_REASON_LABELS.get(code, 'unrecognized reason code; inspect the pinned native definition')}"
            for code in reason_codes
        ) or "None supplied"
        lines.extend([
            f"## Scenario `{row['case_id']}`",
            f"- Test lane: {_LANES[row['lane']]}.",
            f"- Supplied status (unverified): {status}.",
            f"- Fictional source and record: `{source['source_id']}` / `{source['record_id']}`.",
            f"- Snapshot / reviewed versions: `{version}`.",
            f"- Snapshot time: `{source['snapshot_time']}`.",
            f"- Reason codes: {reasons}.",
            "- Report effects: no selection or issue was produced by this report; no assignment, notification, commit, or closure. Source claims remain unverified.",
            "",
        ])
    return "\n".join(lines) + "\n"


def render_pinned_f10_rev4_test_catalog(raw_output: bytes) -> str:
    """Render only the retained F10 rev4 native output with its recorded digest."""
    _require(isinstance(raw_output, bytes), "Pinned F10 input must be the original JSON bytes.")
    actual_sha256 = sha256(raw_output).hexdigest()
    _require(actual_sha256 == _F10_REV4_OUTPUT_SHA256,
             "F10 rev4 output digest differs; inspect and record the new revision before rendering.")
    try:
        result = json.loads(raw_output)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Pinned F10 rev4 output is not valid JSON.") from error
    report = _render_f10_test_catalog(result)
    return report.replace(
        "**Source:** fixed fictional snapshot; no live register read.\n",
        "**Source:** fixed fictional snapshot; no live register read.\n"
        f"**Pinned native result:** F10 revision 4; SHA256 `{actual_sha256}`.\n",
        1,
    )
