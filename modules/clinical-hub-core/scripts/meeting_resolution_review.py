#!/usr/bin/env python3
"""Check a bounded synthetic F15 packet and return review exceptions only.

This module does not retrieve or authenticate sources, establish authority,
adjudicate a transition, accept closure, or write to any record.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any


SCHEMA_VERSION = "f15.review.v1"
MAX_RESPONSES = 32
MAX_HISTORY = 64
MAX_TOKEN_LENGTH = 64
TOKEN = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
DISPOSITIONS = {
    "open", "resolved", "referred", "held", "returned", "superseded",
    "reopened", "implemented", "no_further_action",
}
COMPLETION = {"complete", "incomplete", "unknown"}
RESPONSE_STATES = {"partial", "complete", "disputed", "withdrawn", "delayed"}
RELEVANCE = {"not_reviewed", "relevant", "partial", "irrelevant", "disputed"}
DATE_STATES = {"known", "unknown", "ambiguous"}
SOURCE_CLAIMS = {"current", "superseded", "unknown", "conflicting"}
REASON_CODES = {
    "reopened_for_review", "new_evidence", "disputed_outcome",
    "source_correction", "other_requires_human_reason",
}

ACTION_FIELDS = {
    "action_id", "register_revision", "minutes_record_id", "minutes_revision",
    "current_disposition", "proposed_outcome", "reported_completion",
    "source_currentness_claim", "required_component_ids",
}
RESPONSE_FIELDS = {
    "response_id", "action_id", "response_state", "relevance_review",
    "evidence_ref", "evidence_revision", "date_state", "date_value",
    "component_ids",
}
CLOSURE_FIELDS = {
    "action_id", "reviewer_role_ref", "authority_ref", "decision_ref", "decision_revision",
    "evidence_ref", "date_state", "date_value",
}
HISTORY_FIELDS = {
    "event_id", "action_id", "disposition", "reason_code", "evidence_ref",
    "date_state", "date_value", "prior_event_id",
}
REOPEN_FIELDS = {"reason_code", "prior_closure_ref", "authority_ref", "date_state", "date_value"}


def _exception(code: str, field: str) -> dict[str, str]:
    return {"code": code, "field": field}


def _token(value: Any) -> bool:
    return isinstance(value, str) and len(value) <= MAX_TOKEN_LENGTH and bool(TOKEN.fullmatch(value))


def _date_exceptions(obj: dict[str, Any], field: str) -> list[dict[str, str]]:
    state = obj.get("date_state")
    value = obj.get("date_value")
    if not isinstance(state, str) or state not in DATE_STATES:
        return [_exception("DATE_STATE_UNKNOWN", field + ".date_state")]
    if state != "known":
        if value not in (None, ""):
            return [_exception("DATE_VALUE_WITHOUT_KNOWN_STATE", field + ".date_value")]
        return [_exception("DATE_UNKNOWN" if state == "unknown" else "DATE_AMBIGUOUS", field + ".date_state")]
    if not isinstance(value, str):
        return [_exception("DATE_VALUE_MISSING", field + ".date_value")]
    try:
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        return [_exception("DATE_INVALID_OR_AMBIGUOUS", field + ".date_value")]
    # The date is caller-supplied and remains unverified even when well formed.
    return []


def _unknown_fields(obj: Any, allowed: set[str], field: str) -> list[dict[str, str]]:
    if not isinstance(obj, dict):
        return [_exception("OBJECT_REQUIRED", field)]
    return [_exception("UNSUPPORTED_FIELDS", field)] if set(obj) - allowed else []


def _check_token(obj: dict[str, Any], key: str, path: str, required: bool = True) -> list[dict[str, str]]:
    value = obj.get(key)
    if not required and value in (None, ""):
        return []
    if not _token(value):
        return [_exception("REFERENCE_MISSING_OR_INVALID", path + "." + key)]
    return []


def review_packet(packet: Any) -> dict[str, Any]:
    """Return a deterministic, non-adjudicating review summary for one packet."""
    errors: list[dict[str, str]] = []
    if not isinstance(packet, dict):
        errors.append(_exception("OBJECT_REQUIRED", "packet"))
        packet = {}
    allowed = {"schema_version", "packet_id", "binding", "action", "responses", "closure_claim", "history", "reopen"}
    errors.extend(_unknown_fields(packet, allowed, "packet"))

    packet_id = packet.get("packet_id")
    packet_id_valid = _token(packet_id)
    if not packet_id_valid:
        errors.append(_exception("REFERENCE_MISSING_OR_INVALID", "packet.packet_id"))
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append(_exception("SCHEMA_VERSION_UNSUPPORTED", "packet.schema_version"))

    binding = packet.get("binding")
    if not isinstance(binding, dict):
        errors.append(_exception("OBJECT_REQUIRED", "packet.binding"))
        binding = {}
    binding_fields = {"action_id", "register_revision", "minutes_record_id", "minutes_revision"}
    errors.extend(_unknown_fields(binding, binding_fields, "packet.binding"))
    for key in binding_fields:
        errors.extend(_check_token(binding, key, "packet.binding"))

    action = packet.get("action")
    if not isinstance(action, dict):
        errors.append(_exception("OBJECT_REQUIRED", "packet.action"))
        action = {}
    errors.extend(_unknown_fields(action, ACTION_FIELDS, "packet.action"))
    for key in ("action_id", "register_revision", "minutes_record_id", "minutes_revision"):
        errors.extend(_check_token(action, key, "packet.action"))
    action_id = action.get("action_id") if _token(action.get("action_id")) else None
    register_revision = action.get("register_revision") if _token(action.get("register_revision")) else None
    minutes_id = action.get("minutes_record_id") if _token(action.get("minutes_record_id")) else None
    minutes_revision = action.get("minutes_revision") if _token(action.get("minutes_revision")) else None
    for key, value in (("action_id", action_id), ("register_revision", register_revision),
                       ("minutes_record_id", minutes_id), ("minutes_revision", minutes_revision)):
        bound = binding.get(key)
        if value and _token(bound) and value != bound:
            errors.append(_exception("SOURCE_REFERENCE_MISMATCH", "packet.action." + key))

    current = action.get("current_disposition")
    proposed = action.get("proposed_outcome")
    completion = action.get("reported_completion")
    if not isinstance(current, str) or current not in DISPOSITIONS:
        errors.append(_exception("DISPOSITION_UNKNOWN", "packet.action.current_disposition"))
    if not isinstance(proposed, str) or proposed not in DISPOSITIONS:
        errors.append(_exception("PROPOSED_OUTCOME_UNKNOWN", "packet.action.proposed_outcome"))
    if not isinstance(completion, str) or completion not in COMPLETION:
        errors.append(_exception("COMPLETION_STATE_UNKNOWN", "packet.action.reported_completion"))
    source_claim = action.get("source_currentness_claim")
    if not isinstance(source_claim, str) or source_claim not in SOURCE_CLAIMS:
        errors.append(_exception("SOURCE_CLAIM_UNKNOWN", "packet.action.source_currentness_claim"))
    elif source_claim == "superseded":
        errors.append(_exception("SUPERSESSION_CLAIM_UNVERIFIED", "packet.action.source_currentness_claim"))
    elif source_claim == "conflicting":
        errors.append(_exception("SOURCE_CONFLICT_CLAIM_UNVERIFIED", "packet.action.source_currentness_claim"))
    elif source_claim == "unknown":
        errors.append(_exception("SOURCE_CURRENTNESS_UNKNOWN", "packet.action.source_currentness_claim"))
    errors.append(_exception("SOURCE_CURRENTNESS_UNVERIFIED", "packet.action"))
    errors.append(_exception("TRANSITION_POLICY_UNVERIFIED", "packet.action.proposed_outcome"))
    if completion == "complete":
        errors.append(_exception("REPORTED_COMPLETION_IS_NOT_CLOSURE", "packet.action.reported_completion"))

    required_components = action.get("required_component_ids", [])
    if (not isinstance(required_components, list) or len(required_components) > 32
            or not all(_token(value) for value in required_components)
            or len(set(required_components)) != len(required_components)):
        errors.append(_exception("REQUIRED_COMPONENTS_INVALID", "packet.action.required_component_ids"))
        required_components_set: set[str] = set()
    else:
        required_components_set = set(required_components)

    responses = packet.get("responses", [])
    if not isinstance(responses, list):
        errors.append(_exception("ARRAY_REQUIRED", "packet.responses"))
        responses = []
    if len(responses) > MAX_RESPONSES:
        errors.append(_exception("RESPONSE_LIMIT_EXCEEDED", "packet.responses"))
    response_ids: set[str] = set()
    response_keys: set[tuple[str, str]] = set()
    response_states: set[str] = set()
    covered_components: set[str] = set()
    linked_responses = 0
    for index, response in enumerate(responses[:MAX_RESPONSES]):
        path = f"packet.responses[{index}]"
        errors.extend(_unknown_fields(response, RESPONSE_FIELDS, path))
        if not isinstance(response, dict):
            continue
        for key in ("response_id", "action_id", "evidence_ref", "evidence_revision"):
            errors.extend(_check_token(response, key, path))
        response_id = response.get("response_id")
        if _token(response_id):
            if response_id in response_ids:
                errors.append(_exception("DUPLICATE_KEY_WITHIN_PACKET", path + ".response_id"))
            response_ids.add(response_id)
        response_action = response.get("action_id")
        if action_id and _token(response_action) and response_action != action_id:
            errors.append(_exception("ACTION_REFERENCE_MISMATCH", path + ".action_id"))
        elif action_id and response_action == action_id:
            linked_responses += 1
        state = response.get("response_state")
        if not isinstance(state, str) or state not in RESPONSE_STATES:
            errors.append(_exception("RESPONSE_STATE_UNKNOWN", path + ".response_state"))
        elif state in {"partial", "disputed", "withdrawn", "delayed"}:
            errors.append(_exception("RESPONSE_REQUIRES_HUMAN_REVIEW", path + ".response_state"))
        if isinstance(state, str) and state in RESPONSE_STATES:
            response_states.add(state)
        relevance = response.get("relevance_review")
        if not isinstance(relevance, str) or relevance not in RELEVANCE:
            errors.append(_exception("RELEVANCE_STATE_UNKNOWN", path + ".relevance_review"))
        elif relevance in {"partial", "irrelevant", "disputed"}:
            errors.append(_exception("RELEVANCE_CLAIM_UNVERIFIED", path + ".relevance_review"))
        elif relevance == "not_reviewed":
            errors.append(_exception("RELEVANCE_NOT_REVIEWED", path + ".relevance_review"))
        components = response.get("component_ids", [])
        if not isinstance(components, list) or len(components) > 32 or not all(_token(x) for x in components):
            errors.append(_exception("COMPONENT_REFERENCE_INVALID", path + ".component_ids"))
        elif isinstance(components, list):
            covered_components.update(components)
        key = (str(response_action), str(response.get("evidence_ref")))
        if key in response_keys:
            errors.append(_exception("DUPLICATE_EVIDENCE_WITHIN_PACKET", path + ".evidence_ref"))
        response_keys.add(key)
        errors.extend(_date_exceptions(response, path))
    if len(response_states) > 1:
        errors.append(_exception("MULTIPLE_RESPONSE_STATES_NEED_REVIEW", "packet.responses"))
    if required_components_set - covered_components:
        errors.append(_exception("RESPONSE_COMPONENTS_UNCOVERED", "packet.responses"))
    if not linked_responses and (current == "referred" or proposed in {"resolved", "no_further_action"}):
        errors.append(_exception("NO_LINKED_RESPONSE", "packet.responses"))

    closure = packet.get("closure_claim")
    if closure is not None:
        errors.extend(_unknown_fields(closure, CLOSURE_FIELDS, "packet.closure_claim"))
        if isinstance(closure, dict):
            for key in ("action_id", "reviewer_role_ref", "authority_ref", "decision_ref", "decision_revision", "evidence_ref"):
                errors.extend(_check_token(closure, key, "packet.closure_claim"))
            if action_id and _token(closure.get("action_id")) and closure["action_id"] != action_id:
                errors.append(_exception("ACTION_REFERENCE_MISMATCH", "packet.closure_claim.action_id"))
            if minutes_id and _token(closure.get("decision_ref")) and closure["decision_ref"] != minutes_id:
                errors.append(_exception("MINUTES_REFERENCE_MISMATCH", "packet.closure_claim.decision_ref"))
            if minutes_revision and _token(closure.get("decision_revision")) and closure["decision_revision"] != minutes_revision:
                errors.append(_exception("MINUTES_REVISION_MISMATCH", "packet.closure_claim.decision_revision"))
            errors.extend(_date_exceptions(closure, "packet.closure_claim"))
            errors.append(_exception("AUTHORITY_CLAIM_UNVERIFIED", "packet.closure_claim.authority_ref"))
            errors.append(_exception("DECISION_CLAIM_UNVERIFIED", "packet.closure_claim.decision_ref"))
    elif proposed in {"resolved", "no_further_action"}:
        errors.append(_exception("CLOSURE_PACKET_MISSING", "packet.closure_claim"))
    if proposed in {"resolved", "no_further_action"}:
        errors.append(_exception("CLOSURE_CANNOT_BE_ACCEPTED_BY_VALIDATOR", "packet.action.proposed_outcome"))

    history = packet.get("history", [])
    if not isinstance(history, list):
        errors.append(_exception("ARRAY_REQUIRED", "packet.history"))
        history = []
    if len(history) > MAX_HISTORY:
        errors.append(_exception("HISTORY_LIMIT_EXCEEDED", "packet.history"))
    event_ids: set[str] = set()
    prior_event_ids: set[str] = set()
    prior_keys: set[tuple[str, str]] = set()
    for index, event in enumerate(history[:MAX_HISTORY]):
        path = f"packet.history[{index}]"
        errors.extend(_unknown_fields(event, HISTORY_FIELDS, path))
        if not isinstance(event, dict):
            continue
        for key in ("event_id", "action_id", "evidence_ref"):
            errors.extend(_check_token(event, key, path))
        event_id = event.get("event_id")
        if _token(event_id):
            if event_id in event_ids:
                errors.append(_exception("DUPLICATE_KEY_WITHIN_PACKET", path + ".event_id"))
            event_ids.add(event_id)
        history_action = event.get("action_id")
        if action_id and _token(history_action) and history_action != action_id:
            errors.append(_exception("ACTION_REFERENCE_MISMATCH", path + ".action_id"))
        if not isinstance(event.get("disposition"), str) or event.get("disposition") not in DISPOSITIONS:
            errors.append(_exception("DISPOSITION_UNKNOWN", path + ".disposition"))
        reason = event.get("reason_code")
        if reason is not None and (not isinstance(reason, str) or reason not in REASON_CODES):
            errors.append(_exception("REASON_CODE_UNKNOWN", path + ".reason_code"))
        prior = event.get("prior_event_id")
        if prior is not None and not _token(prior):
            errors.append(_exception("REFERENCE_MISSING_OR_INVALID", path + ".prior_event_id"))
        elif prior is not None and prior not in prior_event_ids:
            errors.append(_exception("HISTORY_LINK_MISSING_OR_OUT_OF_ORDER", path + ".prior_event_id"))
        if _token(history_action) and _token(event.get("evidence_ref")):
            prior_key = (history_action, event["evidence_ref"])
            if prior_key in prior_keys:
                errors.append(_exception("DUPLICATE_EVIDENCE_WITHIN_PACKET", path + ".evidence_ref"))
            prior_keys.add(prior_key)
        errors.extend(_date_exceptions(event, path))
        if _token(event_id):
            prior_event_ids.add(event_id)
    errors.append(_exception("SUPPLIED_HISTORY_COMPLETENESS_UNVERIFIED", "packet.history"))

    reopen = packet.get("reopen")
    if reopen is not None:
        errors.extend(_unknown_fields(reopen, REOPEN_FIELDS, "packet.reopen"))
        if isinstance(reopen, dict):
            for key in ("prior_closure_ref", "authority_ref"):
                errors.extend(_check_token(reopen, key, "packet.reopen"))
            closure_ref = reopen.get("prior_closure_ref")
            if _token(closure_ref) and closure_ref not in event_ids:
                errors.append(_exception("REOPEN_PRIOR_CLOSURE_NOT_IN_SUPPLIED_HISTORY", "packet.reopen.prior_closure_ref"))
            if not isinstance(reopen.get("reason_code"), str) or reopen.get("reason_code") not in REASON_CODES:
                errors.append(_exception("REOPEN_REASON_MISSING_OR_UNKNOWN", "packet.reopen.reason_code"))
            if not history:
                errors.append(_exception("REOPEN_PRIOR_HISTORY_MISSING", "packet.history"))
            errors.extend(_date_exceptions(reopen, "packet.reopen"))
            errors.append(_exception("REOPEN_AUTHORITY_UNVERIFIED", "packet.reopen.authority_ref"))
    elif current == "reopened" or proposed == "reopened":
        errors.append(_exception("REOPEN_PACKET_MISSING", "packet.reopen"))

    # Stable output order makes repeated local checks comparable. No supplied
    # free text or raw unknown key is reflected in the result.
    unique = {(item["code"], item["field"]): item for item in errors}
    exceptions = [unique[key] for key in sorted(unique)]
    return {
        "schema_version": SCHEMA_VERSION,
        "packet_id_valid": packet_id_valid,
        "result": "PROPOSED_FOR_HUMAN_REVIEW",
        "proposed_outcome": proposed if proposed in DISPOSITIONS else None,
        "reported_completion": completion if completion in COMPLETION else None,
        "human_disposition": None,
        "authority_status": "UNVERIFIED",
        "source_currentness": "UNVERIFIED",
        "supplied_history_completeness": "UNVERIFIED",
        "exceptions": exceptions,
    }
