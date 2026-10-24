"""Synthetic cases for the F09 pure proposal preview; no tenant/network access."""
import ast
import copy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from meeting_commit_preview import preview


def case():
    destination = {"accepted": True, "target": "synthetic-register", "schema_ref": "schema-v1",
                   "use_ref": "reviewed-outcome-preview", "acceptance_ref": "acceptance-fixture",
                   "cutover_ref": "cutover-fixture"}
    source = {"status": "approved", "kind": "approved_minutes", "source_ref": "minutes-fixture",
              "revision": "rev-2", "approval_ref": "minute-approval-fixture",
              "passage_ref": "minutes-fixture#p1", "passage_text": "Original synthetic wording",
              "conditions": ["subject to synthetic condition"], "dissent": ["synthetic dissent preserved"]}
    current = {"target": "synthetic-register", "item_id": "LEGACY-001", "version": "v4",
               "wording": "Original synthetic wording", "history": [{"version": "v3", "wording": "Earlier wording"}],
               "issued": False}
    candidate = {"item_id": "LEGACY-001", "source_ref": "minutes-fixture", "source_revision": "rev-2",
                 "before_version": "v4", "passage_ref": "minutes-fixture#p1", "wording": source["passage_text"],
                 "conditions": list(source["conditions"]), "dissent": list(source["dissent"]), "kind": "decision"}
    review = {"disposition": "approve", "reviewer_ref": "reviewer-fixture",
              "authority": {"verified": True, "role": "authorised-reviewer", "evidence_ref": "role-evidence-fixture"},
              "review_evidence_ref": "review-evidence-fixture", "reviewed_at": "2030-01-02T09:00:00+10:00"}
    return destination, source, current, candidate, review


def run(c=None, as_of_date="2030-01-01", **kwargs):
    c = c or case()
    d, s, current, candidate, review = c
    return preview(destination=d, source=s, current=current, candidate=candidate,
                   review=review, as_of_date=as_of_date, **kwargs)


def bound_payload(c, wording=None):
    _, source, _, candidate, review = c
    return {"wording": wording if wording is not None else candidate["wording"],
            "conditions": candidate["conditions"], "dissent": candidate["dissent"],
            "source_ref": source["source_ref"], "source_revision": source["revision"],
            "source_approval_ref": source["approval_ref"], "passage_ref": source["passage_ref"],
            "amendment_authority_ref": review.get("amendment_authority_ref") if review.get("disposition") == "amend" else None,
            "issued_record_correction_ref": review.get("issued_record_correction_ref") if review.get("disposition") == "amend" else None,
            "action": candidate.get("commission") if candidate["kind"] == "action" else None}


def test_eligible_review_is_proposal_only_and_preserves_conditions_dissent_and_history():
    c = case(); original = copy.deepcopy(c)
    out = run(c)
    assert out["state"] == "APPROVED_PROPOSAL"
    assert out["preview_only"] and not out["committed"]
    assert not out["issued"] and not out["assigned"] and not out["notified"] and not out["closed"]
    assert out["after"]["conditions"] == ["subject to synthetic condition"]
    assert out["after"]["dissent"] == ["synthetic dissent preserved"]
    assert out["history"][0]["version"] == "v3"
    assert out["history"][-1]["authority_role"] == "authorised-reviewer"
    assert out["history"][-1]["source_revision"] == "rev-2"
    assert c == original
    assert run()["operation_key"] == run()["operation_key"]
    assert len(out["operation_key"]) == 64


def test_destination_must_be_accepted_for_exact_target_schema_and_use():
    c = case(); c[0]["accepted"] = False
    assert "destination_unaccepted" in {b["code"] for b in run(c)["blockers"]}


def test_decision_log_lookup_cannot_replace_approved_minutes_authority():
    c = case(); c[1]["kind"] = "decision_log"
    assert "source_not_authoritative" in {b["code"] for b in run(c)["blockers"]}


def test_missing_or_draft_or_conflicting_source_blocks():
    for update, expected in [({"status": "draft"}, "source_not_authoritative"),
                            ({"conflict": True}, "source_conflict"),
                            ({"revision": "rev-3"}, "source_version_mismatch")]:
        c = case(); c[1].update(update)
        assert expected in {b["code"] for b in run(c)["blockers"]}


def test_no_disposition_bulk_and_unverified_authority_block():
    c = case(); c[4]["disposition"] = None
    no_response = run(c)
    assert no_response["state"] == "HELD"
    assert "disposition_required" in {b["code"] for b in no_response["blockers"]}
    c = case(); c[4]["dispositions"] = ["approve", "approve"]
    assert "bulk_disposition" in {b["code"] for b in run(c)["blockers"]}
    c = case(); c[4]["authority"]["verified"] = False
    assert "review_authority_missing" in {b["code"] for b in run(c)["blockers"]}


def test_amendment_requires_wording_authority_and_issued_record_route():
    c = case(); c[4]["disposition"] = "amend"
    assert "amendment_incomplete" in {b["code"] for b in run(c)["blockers"]}
    c[4].update(replacement_wording="Amended synthetic wording", amendment_authority_ref="amend-authority")
    assert "amendment_incomplete" not in {b["code"] for b in run(c)["blockers"]}
    c[2]["issued"] = True
    assert "issued_record_immutable" in {b["code"] for b in run(c)["blockers"]}
    c[4]["issued_record_correction_ref"] = "correction-route-fixture"
    assert run(c)["state"] == "AMENDED_PROPOSAL"


def test_conditions_dissent_and_ambiguous_negation_are_never_normalized():
    c = case(); c[3]["conditions"] = []
    assert "conditions_changed" in {b["code"] for b in run(c)["blockers"]}
    c = case(); c[3]["dissent"] = []
    assert "dissent_changed" in {b["code"] for b in run(c)["blockers"]}
    c = case(); c[3]["normalization_requested"] = True
    assert "wording_normalization" in {b["code"] for b in run(c)["blockers"]}


def test_action_needs_commission_accepted_owner_and_explicit_agreed_date():
    c = case(); c[3]["kind"] = "action"
    assert {"commission_unverified", "owner_unverified", "date_unverified"} <= {b["code"] for b in run(c)["blockers"]}
    c[3]["commission"] = {"explicit": True, "authority_ref": "commission-fixture", "meeting_purpose": "commission",
                           "owner_accepted": True, "owner_ref": "owner-fixture", "owner_authority_ref": "owner-authority-fixture",
                           "owner_acceptance_ref": "owner-acceptance-fixture", "date_agreed": True,
                           "date_kind": "due", "date_value": "2030-01-01", "date_authority_ref": "date-fixture"}
    out = run(c)
    assert out["state"] == "APPROVED_PROPOSAL"
    assert out["after"]["action"]["owner_ref"] == "owner-fixture"
    assert out["after"]["action"]["date_value"] == "2030-01-01"
    baseline_key = out["operation_key"]
    c[3]["commission"]["owner_ref"] = "another-owner-fixture"
    assert run(c)["operation_key"] != baseline_key
    c[3]["commission"]["owner_ref"] = "owner-fixture"
    c[3]["commission"]["date_value"] = "2030-01-02"
    assert run(c)["operation_key"] != baseline_key
    c[3]["commission"]["meeting_purpose"] = "discussion"
    assert "not_commissioned" in {b["code"] for b in run(c)["blockers"]}
    c[3]["commission"].update(meeting_purpose="commission", date_value="not-a-date")
    assert "date_invalid" in {b["code"] for b in run(c)["blockers"]}


def test_action_date_validation_uses_explicit_assessment_date_and_preserves_its_basis():
    c = case(); c[3]["kind"] = "action"
    c[3]["commission"] = {"explicit": True, "authority_ref": "commission-fixture", "meeting_purpose": "commission",
                           "owner_accepted": True, "owner_ref": "owner-fixture", "owner_authority_ref": "owner-authority-fixture",
                           "owner_acceptance_ref": "owner-acceptance-fixture", "date_agreed": True,
                           "date_kind": "due", "date_value": "2030-01-01", "date_authority_ref": "date-fixture"}

    same_day = run(c, as_of_date="2030-01-01")
    assert same_day["state"] == "APPROVED_PROPOSAL"
    assert same_day["assessment_date"] == "2030-01-01"
    assert same_day["history"][-1]["assessment_date"] == "2030-01-01"

    c[3]["commission"]["date_value"] = "2030-01-02"
    future = run(c, as_of_date="2030-01-01")
    assert future["state"] == "APPROVED_PROPOSAL"
    rechecked = run(c, as_of_date="2030-01-02")
    assert rechecked["state"] == "APPROVED_PROPOSAL"
    assert future["operation_key"] == rechecked["operation_key"]
    assert rechecked["history"][-1]["assessment_date"] == "2030-01-02"

    c[3]["commission"]["date_value"] = "2029-12-31"
    past = run(c, as_of_date="2030-01-01")
    assert past["state"] == "BLOCKED"
    assert "date_in_past" in {b["code"] for b in past["blockers"]}

    missing = run(c, as_of_date=None)
    assert "assessment_date_required" in {b["code"] for b in missing["blockers"]}
    invalid = run(c, as_of_date="2030-02-30")
    assert "assessment_date_invalid" in {b["code"] for b in invalid["blockers"]}
    assert "date_in_past" not in {b["code"] for b in invalid["blockers"]}
    assert "assessment_date_invalid" in {b["code"] for b in run(c, as_of_date=20300101)["blockers"]}

    c[3]["commission"]["date_value"] = "2030-02-30"
    assert "date_invalid" in {b["code"] for b in run(c)["blockers"]}


def test_source_name_is_not_owner_and_inferred_date_is_not_accepted():
    c = case(); c[3]["kind"] = "action"
    c[3]["commission"] = {"explicit": True, "authority_ref": "commission-fixture", "meeting_purpose": "commission",
                           "owner_accepted": False, "date_agreed": False}
    codes = {b["code"] for b in run(c)["blockers"]}
    assert {"owner_unverified", "date_unverified"} <= codes


def test_duplicate_operation_key_is_bound_to_target_item_version_and_payload():
    c = case(); d, _, current, candidate, review = c
    binding = {"destination": {key: d[key] for key in ("target", "schema_ref", "use_ref", "acceptance_ref", "cutover_ref")},
               "item_id": current["item_id"], "before_version": current["version"],
               "disposition": review["disposition"], "payload": bound_payload(c)}
    returned_key = run(c)["operation_key"]
    assert "duplicate_operation" in {b["code"] for b in run(c, operation_keys=[{"key": returned_key, "binding": binding}])["blockers"]}
    binding["destination"]["target"] = "other-target"
    assert "operation_key_reused" in {b["code"] for b in run(c, operation_keys=[{"key": returned_key, "binding": binding}])["blockers"]}


def test_amendment_key_includes_replacement_and_changed_prior_amendment_needs_correction():
    c = case(); c[4].update(disposition="amend", replacement_wording="Amendment one",
                           amendment_authority_ref="amend-authority")
    first = run(c)
    c2 = case(); c2[4].update(disposition="amend", replacement_wording="Amendment two",
                              amendment_authority_ref="amend-authority")
    second = run(c2)
    assert first["operation_key"] != second["operation_key"]
    binding = {"destination": {key: c2[0][key] for key in ("target", "schema_ref", "use_ref", "acceptance_ref", "cutover_ref")},
               "item_id": c2[2]["item_id"], "before_version": c2[2]["version"],
               "disposition": "amend", "payload": bound_payload(c2, "Amendment one")}
    c2[4]["operation_key"] = first["operation_key"]
    assert "operation_key_unbound" in {b["code"] for b in run(c2, operation_keys=[{"key": first["operation_key"], "binding": binding}])["blockers"]}
    c2[4]["prior_dispositions"] = [{"item_id": "LEGACY-001", "disposition": "amend", "payload": "Amendment one"}]
    assert "review_disagreement" in {b["code"] for b in run(c2)["blockers"]}
    c2[4]["correction_ref"] = "amendment-correction-fixture"
    c2[4].pop("operation_key")
    assert run(c2)["state"] == "AMENDED_PROPOSAL"


def test_amendment_authority_and_issued_correction_refs_bind_key_and_history():
    c = case(); c[2]["issued"] = True
    c[4].update(disposition="amend", replacement_wording="Amended wording",
                amendment_authority_ref="authority-A", issued_record_correction_ref="correction-route-A")
    first = run(c)
    assert first["history"][-1]["amendment_authority_ref"] == "authority-A"
    c[4]["amendment_authority_ref"] = "authority-B"
    assert run(c)["operation_key"] != first["operation_key"]
    c[4]["amendment_authority_ref"] = "authority-A"
    c[4]["issued_record_correction_ref"] = "correction-route-B"
    assert run(c)["operation_key"] != first["operation_key"]


def test_issued_record_correction_reference_must_be_nonempty_text():
    c = case(); c[2]["issued"] = True
    c[4].update(disposition="amend", replacement_wording="Amended wording",
                amendment_authority_ref="authority-A", issued_record_correction_ref=True)
    assert "issued_record_immutable" in {b["code"] for b in run(c)["blockers"]}


def test_same_proposal_key_is_stable_across_reviewers_and_times():
    c = case(); first = run(c)
    c[4]["reviewer_ref"] = "another-reviewer-fixture"
    c[4]["review_evidence_ref"] = "another-review-evidence-fixture"
    c[4]["reviewed_at"] = "2030-01-03T09:00:00+10:00"
    second = run(c)
    assert first["operation_key"] == second["operation_key"]
    assert first["history"][-1]["reviewer_ref"] != second["history"][-1]["reviewer_ref"]


def test_stale_version_id_collision_or_incomplete_history_blocks():
    for field, value in [("before_version", "v3"), ("legacy_id_collision", True), ("history_incomplete", True)]:
        c = case(); c[3][field] = value
        codes = {b["code"] for b in run(c)["blockers"]}
        expected = "stale_version" if field == "before_version" else "id_history_integrity"
        assert expected in codes


def test_conflicting_review_needs_explicit_reconciliation_and_keeps_correction_history():
    c = case(); c[4]["prior_dispositions"] = [{"item_id": "LEGACY-001", "disposition": "hold"}]
    assert "review_disagreement" in {b["code"] for b in run(c)["blockers"]}
    c[4]["correction_ref"] = "reconciliation-fixture"
    out = run(c)
    assert out["state"] == "APPROVED_PROPOSAL"
    assert out["history"][-2]["disposition"] == "hold"


def test_unknown_partial_or_committed_recovery_state_requires_reconciliation():
    c = case(); c[3]["recovery_targets"] = ["minutes", "synthetic-register"]
    for state in ("unknown", "committed", "conflict", "nonsense"):
        assert "reconciliation_required" in {b["code"] for b in run(c, recovery={"minutes": "absent", "synthetic-register": state})["blockers"]}


def test_missing_recovery_destination_blocks():
    c = case(); c[3]["recovery_targets"] = ["minutes", "synthetic-register"]
    assert "recovery_targets_incomplete" in {b["code"] for b in run(c, recovery={"minutes": "absent"})["blockers"]}


def test_malformed_recovery_targets_cannot_omit_authoritative_destination():
    for targets in ([], ["foreign-target"], ["synthetic-register", "synthetic-register"],
                    ["synthetic-register", ""], ["synthetic-register", "   "],
                    ["synthetic-register", None], "synthetic-register"):
        c = case(); c[3]["recovery_targets"] = targets
        original = copy.deepcopy(c)
        recovery = {target: "absent" for target in targets if isinstance(target, str)} if isinstance(targets, list) else {}
        out = run(c, recovery=recovery)
        assert out["state"] == "BLOCKED"
        assert "recovery_targets_invalid" in {b["code"] for b in out["blockers"]}
        assert not out["committed"] and c == original


def test_declared_recovery_requires_observed_destination_states():
    c = case(); c[3]["recovery_targets"] = ["minutes", "synthetic-register"]
    out = run(c)
    assert out["state"] == "BLOCKED"
    assert "reconciliation_required" in {b["code"] for b in out["blockers"]}
    assert run(c, recovery={"minutes": "absent", "synthetic-register": "absent"})["state"] == "APPROVED_PROPOSAL"
    assert "recovery_targets_incomplete" in {b["code"] for b in run(c, recovery={
        "minutes": "absent", "synthetic-register": "absent", "extra": "absent"})["blockers"]}
    assert run()["state"] == "APPROVED_PROPOSAL"


def test_arbitrary_caller_key_cannot_bypass_generated_key_replay_detection():
    c = case(); c[4]["operation_key"] = "fresh-unrelated-key"
    assert "operation_key_unbound" in {b["code"] for b in run(c)["blockers"]}


def test_destination_requires_cutover_evidence_and_boolean_acceptance():
    c = case(); c[0].pop("cutover_ref")
    assert "destination_unaccepted" in {b["code"] for b in run(c)["blockers"]}
    c = case(); c[0]["accepted"] = "yes"
    assert "destination_unaccepted" in {b["code"] for b in run(c)["blockers"]}


def test_hold_and_reject_preserve_item_and_provenance_without_deleting_it():
    c = case(); c[4]["disposition"] = "hold"
    assert run(c)["state"] == "HELD"
    c[4]["disposition"] = "reject"
    out = run(c)
    assert out["state"] == "REJECTED_PROPOSAL"
    assert out["before"]["wording"] == out["after"]["wording"]
    assert out["source"]["ref"] == "minutes-fixture"


def test_preview_source_has_no_network_or_filesystem_adapter_imports():
    tree = ast.parse((ROOT / "scripts/meeting_commit_preview.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "datetime", "hashlib", "json", "typing"}
    assert "date.today()" not in (ROOT / "scripts/meeting_commit_preview.py").read_text()


def test_exact_source_passage_unknown_kind_and_malformed_authority_fail_closed():
    c = case(); c[3]["wording"] = "Invented or omitted synthetic text"
    assert "source_wording_mismatch" in {b["code"] for b in run(c)["blockers"]}
    c = case(); c[3]["kind"] = "unknown"
    assert "item_kind_unknown" in {b["code"] for b in run(c)["blockers"]}
    c = case(); c[4]["authority"] = None
    assert "input_shape_invalid" in {b["code"] for b in run(c)["blockers"]}


def test_action_owner_identity_is_required_and_exact_particulars_are_returned():
    c = case(); c[3]["kind"] = "action"
    c[3]["commission"] = {"explicit": True, "authority_ref": "commission-fixture", "meeting_purpose": "commission",
                           "owner_accepted": True, "owner_authority_ref": "owner-authority-fixture",
                           "owner_acceptance_ref": "owner-acceptance-fixture", "date_agreed": True,
                           "date_kind": "review", "date_value": "2030-02-01", "date_authority_ref": "date-fixture"}
    assert "owner_unverified" in {b["code"] for b in run(c)["blockers"]}


def test_action_owner_date_source_qualifier_and_dissent_changes_bind_distinct_keys():
    c = case(); c[3]["kind"] = "action"
    c[3]["commission"] = {"explicit": True, "authority_ref": "commission-fixture", "meeting_purpose": "commission",
                           "owner_accepted": True, "owner_ref": "owner-A", "owner_authority_ref": "owner-authority-A",
                           "owner_acceptance_ref": "owner-acceptance-A", "date_agreed": True,
                           "date_kind": "due", "date_value": "2030-03-01", "date_authority_ref": "date-fixture"}
    baseline = run(c)["operation_key"]
    c[3]["commission"]["owner_ref"] = "owner-B"
    assert run(c)["operation_key"] != baseline
    c[3]["commission"]["owner_ref"] = "owner-A"
    c[3]["commission"]["date_value"] = "2030-03-02"
    assert run(c)["operation_key"] != baseline
    c[3]["commission"]["date_value"] = "2030-03-01"
    c[3]["dissent"].append("additional synthetic dissent")
    assert "dissent_changed" in {b["code"] for b in run(c)["blockers"]}
