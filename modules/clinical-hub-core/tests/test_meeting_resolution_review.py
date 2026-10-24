from copy import deepcopy
import importlib.util
from pathlib import Path


MODULE = Path(__file__).parents[1] / "scripts/meeting_resolution_review.py"
spec = importlib.util.spec_from_file_location("meeting_resolution_review", MODULE)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def packet():
    return {
        "schema_version": review.SCHEMA_VERSION,
        "packet_id": "SYN-PACKET-1",
        "binding": {
            "action_id": "SYN-ACTION-1",
            "register_revision": "SYN-REG-1",
            "minutes_record_id": "SYN-MINUTES-1",
            "minutes_revision": "SYN-MIN-REV-1",
        },
        "action": {
            "action_id": "SYN-ACTION-1",
            "register_revision": "SYN-REG-1",
            "minutes_record_id": "SYN-MINUTES-1",
            "minutes_revision": "SYN-MIN-REV-1",
            "current_disposition": "referred",
            "proposed_outcome": "returned",
            "reported_completion": "incomplete",
            "source_currentness_claim": "current",
            "required_component_ids": ["SYN-COMPONENT-1", "SYN-COMPONENT-2"],
        },
        "responses": [{
            "response_id": "SYN-RESPONSE-1",
            "action_id": "SYN-ACTION-1",
            "response_state": "complete",
            "relevance_review": "not_reviewed",
            "evidence_ref": "SYN-EVIDENCE-1",
            "evidence_revision": "SYN-EVIDENCE-REV-1",
            "date_state": "unknown",
            "date_value": None,
            "component_ids": ["SYN-COMPONENT-1"],
        }],
        "closure_claim": None,
        "history": [],
        "reopen": None,
    }


def codes(result):
    return {entry["code"] for entry in result["exceptions"]}


def test_result_is_always_proposed_and_authority_and_sources_stay_unverified():
    result = review.review_packet(packet())
    assert result["result"] == "PROPOSED_FOR_HUMAN_REVIEW"
    assert result["human_disposition"] is None
    assert result["authority_status"] == "UNVERIFIED"
    assert result["source_currentness"] == "UNVERIFIED"
    assert result["supplied_history_completeness"] == "UNVERIFIED"
    assert {"TRANSITION_POLICY_UNVERIFIED", "SOURCE_CURRENTNESS_UNVERIFIED"} <= codes(result)


def test_binding_and_nested_action_references_must_match_supplied_snapshot():
    candidate = packet()
    candidate["action"]["register_revision"] = "SYN-REG-STALE"
    candidate["responses"][0]["action_id"] = "SYN-OTHER-ACTION"
    result = review.review_packet(candidate)
    assert "SOURCE_REFERENCE_MISMATCH" in codes(result)
    assert "ACTION_REFERENCE_MISMATCH" in codes(result)
    assert result["result"] == "PROPOSED_FOR_HUMAN_REVIEW"


def test_reported_completion_without_closure_evidence_never_resolves():
    candidate = packet()
    candidate["action"]["reported_completion"] = "complete"
    candidate["action"]["proposed_outcome"] = "resolved"
    candidate["responses"] = []
    result = review.review_packet(candidate)
    assert "REPORTED_COMPLETION_IS_NOT_CLOSURE" in codes(result)
    assert "NO_LINKED_RESPONSE" in codes(result)
    assert "CLOSURE_PACKET_MISSING" in codes(result)
    assert "CLOSURE_CANNOT_BE_ACCEPTED_BY_VALIDATOR" in codes(result)
    assert result["human_disposition"] is None


def test_partial_disputed_and_irrelevant_response_claims_are_separate_exceptions():
    candidate = packet()
    candidate["responses"][0]["response_state"] = "partial"
    candidate["responses"][0]["relevance_review"] = "irrelevant"
    result = review.review_packet(candidate)
    assert "RESPONSE_REQUIRES_HUMAN_REVIEW" in codes(result)
    assert "RELEVANCE_CLAIM_UNVERIFIED" in codes(result)
    candidate["responses"][0]["response_state"] = "disputed"
    assert "RESPONSE_REQUIRES_HUMAN_REVIEW" in codes(review.review_packet(candidate))


def test_component_partial_coverage_and_delayed_or_withdrawn_responses_stay_open():
    candidate = packet()
    candidate["responses"][0]["response_state"] = "delayed"
    result = review.review_packet(candidate)
    assert "RESPONSE_REQUIRES_HUMAN_REVIEW" in codes(result)
    assert "RESPONSE_COMPONENTS_UNCOVERED" in codes(result)
    assert result["human_disposition"] is None
    candidate["responses"][0]["response_state"] = "withdrawn"
    assert "RESPONSE_REQUIRES_HUMAN_REVIEW" in codes(review.review_packet(candidate))


def test_closure_claim_references_do_not_prove_authority_or_acceptance():
    candidate = packet()
    candidate["action"]["proposed_outcome"] = "resolved"
    candidate["closure_claim"] = {
        "action_id": "SYN-ACTION-1",
        "reviewer_role_ref": "SYN-ROLE-1",
        "authority_ref": "SYN-AUTH-1",
        "decision_ref": "SYN-MINUTES-1",
        "decision_revision": "SYN-MIN-REV-1",
        "evidence_ref": "SYN-EVIDENCE-1",
        "date_state": "unknown",
        "date_value": None,
    }
    result = review.review_packet(candidate)
    assert "AUTHORITY_CLAIM_UNVERIFIED" in codes(result)
    assert "DECISION_CLAIM_UNVERIFIED" in codes(result)
    assert "DATE_UNKNOWN" in codes(result)
    assert result["human_disposition"] is None
    assert result["authority_status"] == "UNVERIFIED"


def test_minutes_revision_mismatch_and_superseded_source_claim_fail_closed():
    candidate = packet()
    candidate["action"]["source_currentness_claim"] = "superseded"
    candidate["action"]["minutes_revision"] = "SYN-MIN-REV-2"
    result = review.review_packet(candidate)
    assert "SOURCE_REFERENCE_MISMATCH" in codes(result)
    assert "SUPERSESSION_CLAIM_UNVERIFIED" in codes(result)


def test_reopen_needs_prior_supplied_history_reason_and_authority_reference():
    candidate = packet()
    candidate["action"]["current_disposition"] = "reopened"
    candidate["reopen"] = {
        "reason_code": "new_evidence",
        "prior_closure_ref": "SYN-CLOSURE-1",
        "authority_ref": "SYN-AUTH-1",
        "date_state": "ambiguous",
        "date_value": None,
    }
    result = review.review_packet(candidate)
    assert "REOPEN_PRIOR_HISTORY_MISSING" in codes(result)
    assert "REOPEN_PRIOR_CLOSURE_NOT_IN_SUPPLIED_HISTORY" in codes(result)
    assert "REOPEN_AUTHORITY_UNVERIFIED" in codes(result)
    assert "DATE_AMBIGUOUS" in codes(result)


def test_history_duplicate_keys_and_out_of_order_links_are_detected_without_rewriting():
    candidate = packet()
    base = {
        "action_id": "SYN-ACTION-1",
        "disposition": "referred",
        "reason_code": "new_evidence",
        "evidence_ref": "SYN-EVIDENCE-H-1",
        "date_state": "unknown",
        "date_value": None,
    }
    candidate["history"] = [
        {**base, "event_id": "SYN-EVENT-1", "prior_event_id": None},
        {**base, "event_id": "SYN-EVENT-1", "prior_event_id": "SYN-EVENT-LATER"},
    ]
    result = review.review_packet(candidate)
    assert "DUPLICATE_KEY_WITHIN_PACKET" in codes(result)
    assert "DUPLICATE_EVIDENCE_WITHIN_PACKET" in codes(result)
    assert "HISTORY_LINK_MISSING_OR_OUT_OF_ORDER" in codes(result)
    assert len(candidate["history"]) == 2


def test_unknown_or_malformed_values_return_exceptions_without_crashing_or_echoing():
    candidate = packet()
    candidate["action"]["current_disposition"] = {"private": "synthetic narrative"}
    candidate["responses"][0]["response_state"] = ["unexpected"]
    candidate["private narrative from source"] = "do not echo this"
    result = review.review_packet(candidate)
    assert "DISPOSITION_UNKNOWN" in codes(result)
    assert "RESPONSE_STATE_UNKNOWN" in codes(result)
    assert "UNSUPPORTED_FIELDS" in codes(result)
    assert "synthetic narrative" not in repr(result)
    assert "private narrative from source" not in repr(result)
    assert "SYN-PACKET-1" not in repr(result)


def test_duplicate_response_ids_are_scoped_to_packet_and_output_is_deterministic():
    candidate = packet()
    candidate["responses"].append(deepcopy(candidate["responses"][0]))
    first = review.review_packet(candidate)
    second = review.review_packet(candidate)
    assert "DUPLICATE_KEY_WITHIN_PACKET" in codes(first)
    assert first == second


def test_unknown_dates_remain_unknown_and_invalid_dates_are_not_normalized():
    candidate = packet()
    candidate["responses"][0]["date_state"] = "known"
    candidate["responses"][0]["date_value"] = "2099-2-01"
    result = review.review_packet(candidate)
    assert "DATE_INVALID_OR_AMBIGUOUS" in codes(result)
    assert result["source_currentness"] == "UNVERIFIED"
