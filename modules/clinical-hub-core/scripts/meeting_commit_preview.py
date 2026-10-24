"""Pure proposal preview for synthetic reviewed meeting outcomes.

This module deliberately has no network, filesystem, connector, or persistence
adapter. A proposal returned here is not a register write or an approval.
"""
from __future__ import annotations

import json
from datetime import date, datetime
import hashlib
from typing import Any


DISPOSITIONS = {"approve", "amend", "hold", "reject"}
RECOVERY_STATES = {"absent", "committed", "unknown", "conflict"}


def _block(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _zoned_timestamp(value: Any) -> bool:
    if not _nonempty(value):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except (ValueError, TypeError, AttributeError):
        return False


def preview(*, destination: dict[str, Any], source: dict[str, Any], current: dict[str, Any],
            candidate: dict[str, Any], review: dict[str, Any],
            operation_keys: list[dict[str, Any]] | None = None,
            recovery: dict[str, str] | None = None,
            as_of_date: str | None = None) -> dict[str, Any]:
    """Return one synthetic item proposal or explicit blockers, without mutation.

    All authority and acceptance values are supplied evidence declarations. This
    function validates their shape and consistency; it cannot authenticate them.
    Action-date checks require an explicit ISO assessment date. The caller must
    supply the applicable local calendar date; this preview does not authenticate
    its freshness or infer one from the host clock.
    """
    blockers: list[dict[str, str]] = []
    inputs = {"destination": destination, "source": source, "current": current,
              "candidate": candidate, "review": review}
    invalid = [name for name, value in inputs.items() if not isinstance(value, dict)]
    if invalid:
        return {"state": "BLOCKED", "preview_only": True, "committed": False,
                "item_id": None, "operation_key": None,
                "blockers": [_block("input_shape_invalid", f"Expected object inputs for: {', '.join(invalid)}.")]}
    shape_problems = []
    if not _string_list(source.get("conditions", [])) or not _string_list(source.get("dissent", [])):
        shape_problems.append("source conditions/dissent must be string lists")
    if not _string_list(candidate.get("conditions", [])) or not _string_list(candidate.get("dissent", [])):
        shape_problems.append("candidate conditions/dissent must be string lists")
    if not isinstance(current.get("history", []), list) or not all(isinstance(x, dict) for x in current.get("history", [])):
        shape_problems.append("current history must be a list of objects")
    if not isinstance(review.get("authority", {}), dict):
        shape_problems.append("review authority must be an object")
    if not isinstance(review.get("prior_dispositions", []), list) or not all(
            isinstance(x, dict) for x in review.get("prior_dispositions", [])):
        shape_problems.append("prior dispositions must be a list of objects")
    if review.get("dispositions") is not None and not isinstance(review.get("dispositions"), list):
        shape_problems.append("bulk disposition input must be a list")
    if review.get("disposition") is not None and not isinstance(review.get("disposition"), str):
        shape_problems.append("disposition must be a single string value")
    if not isinstance(candidate.get("commission", {}), dict):
        shape_problems.append("commission particulars must be an object")
    if candidate.get("kind") is not None and not isinstance(candidate.get("kind"), str):
        shape_problems.append("candidate kind must be a string")
    commission = candidate.get("commission", {})
    if isinstance(commission, dict):
        for field in ("meeting_purpose", "date_kind"):
            if commission.get(field) is not None and not isinstance(commission.get(field), str):
                shape_problems.append(f"commission {field} must be a string")
    if operation_keys is not None and (not isinstance(operation_keys, list) or not all(isinstance(x, dict) for x in operation_keys)):
        shape_problems.append("operation key history must be a list of objects")
    if recovery is not None and not isinstance(recovery, dict):
        shape_problems.append("recovery states must be an object")
    if recovery is not None and isinstance(recovery, dict) and not all(isinstance(v, str) for v in recovery.values()):
        shape_problems.append("recovery states must be strings")
    if shape_problems:
        return {"state": "BLOCKED", "preview_only": True, "committed": False,
                "item_id": candidate.get("item_id"), "operation_key": None,
                "blockers": [_block("input_shape_invalid", problem) for problem in shape_problems]}

    selected_id = candidate.get("item_id")

    if destination.get("accepted") is not True or not all(_nonempty(destination.get(k)) for k in
            ("target", "schema_ref", "use_ref", "acceptance_ref", "cutover_ref")):
        blockers.append(_block("destination_unaccepted", "Exact destination, schema, use, acceptance and cutover evidence are required."))
    if destination.get("target") != current.get("target"):
        blockers.append(_block("destination_mismatch", "Candidate target does not match the current item target."))

    if source.get("status") != "approved" or source.get("kind") != "approved_minutes":
        blockers.append(_block("source_not_authoritative", "Only an explicitly approved minutes source may support this proposal."))
    if not all(_nonempty(source.get(k)) for k in ("source_ref", "revision", "approval_ref")):
        blockers.append(_block("source_incomplete", "Source identity, revision and approval evidence are required."))
    if not all(_nonempty(source.get(k)) for k in ("passage_ref", "passage_text")):
        blockers.append(_block("source_passage_missing", "The exact approved source passage and its reference are required."))
    if source.get("conflict"):
        blockers.append(_block("source_conflict", "Conflicting source evidence requires human reconciliation."))
    if candidate.get("source_ref") != source.get("source_ref") or candidate.get("source_revision") != source.get("revision"):
        blockers.append(_block("source_version_mismatch", "Candidate source reference or revision is stale or mismatched."))
    if candidate.get("passage_ref") != source.get("passage_ref") or candidate.get("wording") != source.get("passage_text"):
        blockers.append(_block("source_wording_mismatch", "Candidate wording must match the exact cited approved source passage."))

    if not _nonempty(selected_id) or selected_id != current.get("item_id"):
        blockers.append(_block("item_id_mismatch", "A stable existing item ID must match exactly; replacement IDs are not minted."))
    if not _nonempty(current.get("version")) or candidate.get("before_version") != current.get("version"):
        blockers.append(_block("stale_version", "The current item version changed after the candidate was prepared."))
    if not _nonempty(current.get("wording")) or not _nonempty(candidate.get("wording")):
        blockers.append(_block("wording_missing", "Original and proposed wording must both be present."))
    if candidate.get("legacy_id_collision") or candidate.get("history_incomplete"):
        blockers.append(_block("id_history_integrity", "Legacy ID collision or missing history blocks the proposal."))

    if isinstance(review.get("dispositions"), list):
        blockers.append(_block("bulk_disposition", "Review is per item; multi-item or bulk disposition is not supported."))
    disposition = review.get("disposition")
    if disposition is None or disposition not in DISPOSITIONS:
        blockers.append(_block("disposition_required", "An explicit valid per-item disposition is required; no response remains held."))
    authority = review.get("authority", {})
    if not isinstance(authority, dict):
        authority = {}
    if disposition is not None and not (authority.get("verified") is True and _nonempty(authority.get("role"))
            and _nonempty(authority.get("evidence_ref")) and _nonempty(review.get("reviewer_ref"))
            and _nonempty(review.get("review_evidence_ref")) and _zoned_timestamp(review.get("reviewed_at"))):
        blockers.append(_block("review_authority_missing", "Verified role-specific review authority and reviewer evidence are required."))
    prior_reviews = review.get("prior_dispositions", [])
    if any(r.get("item_id") != selected_id for r in prior_reviews if isinstance(r, dict)):
        blockers.append(_block("review_item_conflict", "Review history contains another item; resolve conflicting dispositions individually."))
    effective_wording = review.get("replacement_wording") if disposition == "amend" else candidate.get("wording")
    changed_prior = [r for r in prior_reviews if r.get("item_id") == selected_id and
                     (r.get("disposition") != disposition or
                      r.get("payload", r.get("replacement_wording", r.get("wording"))) != effective_wording)]
    if changed_prior:
        if not _nonempty(review.get("correction_ref")):
            blockers.append(_block("review_disagreement", "A changed or conflicting prior disposition needs an explicit correction/reconciliation reference."))

    if disposition == "amend" and (not _nonempty(review.get("replacement_wording"))
                                     or not _nonempty(review.get("amendment_authority_ref"))):
        blockers.append(_block("amendment_incomplete", "An amendment needs replacement wording and explicit amendment authority."))
    if (disposition in {"approve", "amend"} and current.get("issued")
            and effective_wording != current.get("wording")
            and not _nonempty(review.get("issued_record_correction_ref"))):
        blockers.append(_block("issued_record_immutable", "Issued wording cannot be replaced without a separately evidenced correction route."))

    if source.get("conditions", []) != candidate.get("conditions", []):
        blockers.append(_block("conditions_changed", "Conditions and qualifiers must be preserved exactly."))
    if source.get("dissent", []) != candidate.get("dissent", []):
        blockers.append(_block("dissent_changed", "Recorded dissent must be preserved exactly."))
    if candidate.get("normalization_requested"):
        blockers.append(_block("wording_normalization", "Ambiguous or negated wording cannot be normalized automatically."))

    if candidate.get("kind") not in {"decision", "action"}:
        blockers.append(_block("item_kind_unknown", "Candidate kind must be explicitly classified as decision or action."))
    if candidate.get("kind") == "action":
        commission = candidate.get("commission", {})
        if not isinstance(commission, dict):
            commission = {}
        if commission.get("explicit") is not True or not _nonempty(commission.get("authority_ref")):
            blockers.append(_block("commission_unverified", "An explicit commissioned-action decision and authority evidence are required."))
        if commission.get("meeting_purpose") not in {"decision", "commission"}:
            blockers.append(_block("not_commissioned", "Discussion or for-noting material is not an issued action."))
        if (commission.get("owner_accepted") is not True or not _nonempty(commission.get("owner_ref"))
                or not _nonempty(commission.get("owner_authority_ref"))
                or not _nonempty(commission.get("owner_acceptance_ref"))):
            blockers.append(_block("owner_unverified", "A person named in source text is not an accepted accountable owner."))
        if commission.get("date_agreed") is not True or commission.get("date_kind") not in {"due", "review"} \
                or not _nonempty(commission.get("date_value")) or not _nonempty(commission.get("date_authority_ref")):
            blockers.append(_block("date_unverified", "An explicitly agreed due or review date is required; dates are not inferred."))
        assessment_date = None
        if as_of_date is None or as_of_date == "":
            blockers.append(_block("assessment_date_required", "Provide an explicit assessment date; the system clock is not used."))
        elif not _nonempty(as_of_date):
            blockers.append(_block("assessment_date_invalid", "Assessment date must be a valid ISO calendar date."))
        else:
            try:
                assessment_date = date.fromisoformat(as_of_date)
            except ValueError:
                blockers.append(_block("assessment_date_invalid", "Assessment date must be a valid ISO calendar date."))
        if _nonempty(commission.get("date_value")):
            try:
                action_date = date.fromisoformat(commission["date_value"])
                if assessment_date is not None and action_date < assessment_date:
                    blockers.append(_block("date_in_past", "An agreed due or review date in the past requires human reconciliation."))
            except ValueError:
                blockers.append(_block("date_invalid", "Agreed due/review dates must be valid ISO calendar dates."))

    destination_binding = {key: destination.get(key) for key in
                          ("target", "schema_ref", "use_ref", "acceptance_ref", "cutover_ref")}
    proposed_payload = {
        "wording": effective_wording,
        "conditions": candidate.get("conditions", []),
        "dissent": candidate.get("dissent", []),
        "source_ref": source.get("source_ref"),
        "source_revision": source.get("revision"),
        "source_approval_ref": source.get("approval_ref"),
        "passage_ref": source.get("passage_ref"),
        "authority_role": authority.get("role"),
        "authority_ref": authority.get("evidence_ref"),
        "reviewer_ref": review.get("reviewer_ref"),
        "review_evidence_ref": review.get("review_evidence_ref"),
        "reviewed_at": review.get("reviewed_at"),
        "correction_ref": review.get("correction_ref"),
        "amendment_authority_ref": review.get("amendment_authority_ref") if disposition == "amend" else None,
        "issued_record_correction_ref": review.get("issued_record_correction_ref") if disposition in {"approve", "amend"} else None,
        "action": candidate.get("commission") if candidate.get("kind") == "action" else None,
    }
    # Keep the idempotency identity stable across a retry by another reviewer or
    # at another time. Reviewer evidence stays in the preview/history, while the
    # key binds the exact target and proposed semantic payload.
    key_payload = {
        key: proposed_payload[key] for key in (
            "wording", "conditions", "dissent", "source_ref", "source_revision",
            "source_approval_ref", "passage_ref", "amendment_authority_ref",
            "issued_record_correction_ref", "action",
        )
    }
    operation = {
        "destination": destination_binding, "item_id": selected_id,
        "before_version": current.get("version"), "disposition": disposition,
        "payload": key_payload,
    }
    canonical_operation = json.dumps(operation, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    generated_key = hashlib.sha256(canonical_operation.encode("utf-8")).hexdigest()
    operation_key = generated_key
    if _nonempty(review.get("operation_key")) and review["operation_key"] != generated_key:
        blockers.append(_block("operation_key_unbound", "Operation key must equal the deterministic key for this target, ID, version, disposition and payload."))
    key_binding = {"destination": destination_binding, "item_id": selected_id,
                   "before_version": current.get("version"), "disposition": disposition,
                   "payload": key_payload}
    if operation_keys is not None:
        for previous in operation_keys:
            if previous.get("key") == operation_key:
                if previous.get("binding") != key_binding:
                    blockers.append(_block("operation_key_reused", "An operation key cannot be reused with a different target, ID, version or payload."))
                else:
                    blockers.append(_block("duplicate_operation", "This exact operation key already has a proposal; do not replay it."))

    if recovery is not None or "recovery_targets" in candidate:
        expected_targets = candidate.get("recovery_targets", [destination.get("target")])
        valid_targets = (isinstance(expected_targets, list) and bool(expected_targets)
                         and all(_nonempty(target) for target in expected_targets)
                         and len(set(expected_targets)) == len(expected_targets)
                         and destination.get("target") in expected_targets)
        if not valid_targets:
            blockers.append(_block("recovery_targets_invalid", "Recovery destinations must be unique nonblank names and include the authoritative destination."))
        if recovery is None:
            blockers.append(_block("reconciliation_required", "An explicit recovery declaration requires observed state for every affected destination."))
        elif valid_targets and set(recovery) != set(expected_targets):
            blockers.append(_block("recovery_targets_incomplete", "Recovery state must cover every expected affected destination exactly."))
        for target, state in (recovery or {}).items():
            if state not in RECOVERY_STATES or state != "absent":
                blockers.append(_block("reconciliation_required", f"Destination {target!r} is {state!r}; inspect before any further action."))
    if disposition is None:
        substantive = [b for b in blockers if b["code"] != "disposition_required"]
        return {"state": "BLOCKED" if substantive else "HELD", "preview_only": True,
                "committed": False, "item_id": selected_id, "operation_key": operation_key,
                "assessment_date": as_of_date, "blockers": blockers}
    if blockers:
        return {"state": "BLOCKED", "preview_only": True, "committed": False,
                "item_id": selected_id, "operation_key": operation_key,
                "assessment_date": as_of_date, "blockers": blockers}

    if disposition == "hold":
        state = "HELD"
        proposed_wording = current["wording"]
    elif disposition == "reject":
        state = "REJECTED_PROPOSAL"
        proposed_wording = current["wording"]
    elif disposition == "amend":
        state = "AMENDED_PROPOSAL"
        proposed_wording = review["replacement_wording"]
    else:
        state = "APPROVED_PROPOSAL"
        proposed_wording = candidate["wording"]

    return {
        "state": state,
        "preview_only": True,
        "committed": False,
        "issued": False,
        "assigned": False,
        "notified": False,
        "closed": False,
        "item_id": selected_id,
        "assessment_date": as_of_date,
        "destination": destination_binding,
        "source": {"ref": source["source_ref"], "revision": source["revision"],
                   "approval_ref": source["approval_ref"], "passage_ref": source["passage_ref"]},
        "authority": {"role": authority["role"], "evidence_ref": authority["evidence_ref"]},
        "before": {"version": current["version"], "wording": current["wording"]},
        "after": {"wording": proposed_wording, "conditions": source.get("conditions", []),
                  "dissent": source.get("dissent", []),
                  "action": candidate.get("commission") if candidate.get("kind") == "action" else None},
        "history": list(current.get("history", [])) + list(prior_reviews) + [{
            "item_id": selected_id, "disposition": disposition,
            "reviewer_ref": review["reviewer_ref"], "authority_role": authority["role"],
            "authority_ref": authority["evidence_ref"],
            "amendment_authority_ref": proposed_payload["amendment_authority_ref"],
            "issued_record_correction_ref": proposed_payload["issued_record_correction_ref"],
            "source_ref": source["source_ref"], "source_revision": source["revision"],
            "passage_ref": source["passage_ref"], "before_version": current["version"],
            "destination": destination_binding,
            "assessment_date": as_of_date,
            "correction_ref": review.get("correction_ref"), "payload": effective_wording,
            "review_evidence_ref": review["review_evidence_ref"], "reviewed_at": review["reviewed_at"],
        }],
        "operation_key": operation_key,
        "blockers": [],
    }
