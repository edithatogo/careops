"""Issued-wording correction contract; synthetic preview only, no tenant calls."""
from copy import deepcopy

import pytest

from scripts.meeting_commit_preview import preview


def issued_case(disposition="approve", changed=True):
    original = "Issued fictional wording"
    proposed = "Corrected fictional wording" if changed else original
    return dict(
        destination=dict(accepted=True, target="fixture-register", schema_ref="schema-1",
                         use_ref="reviewed-commit", acceptance_ref="acceptance-1", cutover_ref="cutover-1"),
        source=dict(status="approved", kind="approved_minutes", source_ref="fixture-minutes",
                    revision="2", approval_ref="minutes-approval", passage_ref="fixture-minutes#p1",
                    passage_text=proposed, conditions=[], dissent=[]),
        current=dict(target="fixture-register", item_id="LEGACY-001", version="4",
                     wording=original, issued=True, history=[dict(version="3", wording="Prior wording")]),
        candidate=dict(item_id="LEGACY-001", source_ref="fixture-minutes", source_revision="2",
                       before_version="4", passage_ref="fixture-minutes#p1", wording=proposed,
                       conditions=[], dissent=[], kind="decision"),
        review=dict(disposition=disposition, reviewer_ref="fixture-reviewer",
                    authority=dict(verified=True, role="authorised-reviewer", evidence_ref="role-1"),
                    review_evidence_ref="review-1", reviewed_at="2030-01-02T09:00:00+10:00"),
    )


@pytest.mark.parametrize("disposition", ["approve", "amend"])
@pytest.mark.parametrize("correction", [None, "", "   ", True])
def test_changed_issued_wording_requires_text_correction_reference(disposition, correction):
    case = issued_case(disposition)
    if disposition == "amend":
        case["review"].update(replacement_wording="Reviewed amendment", amendment_authority_ref="amend-1")
    if correction is not None:
        case["review"]["issued_record_correction_ref"] = correction
    original = deepcopy(case)
    result = preview(**case)
    assert result["state"] == "BLOCKED"
    assert "issued_record_immutable" in {b["code"] for b in result["blockers"]}
    assert result["committed"] is False
    assert case == original


@pytest.mark.parametrize("disposition", ["approve", "amend"])
def test_correction_reference_binds_operation_and_preserved_history(disposition):
    case = issued_case(disposition)
    if disposition == "amend":
        case["review"].update(replacement_wording="Reviewed amendment", amendment_authority_ref="amend-1")
    case["review"]["issued_record_correction_ref"] = "correction-route-A"
    first = preview(**case)
    assert first["state"] == ("APPROVED_PROPOSAL" if disposition == "approve" else "AMENDED_PROPOSAL")
    assert first["history"][-1]["issued_record_correction_ref"] == "correction-route-A"
    assert first["history"][:-1] == case["current"]["history"]
    case["review"]["issued_record_correction_ref"] = "correction-route-B"
    second = preview(**case)
    assert first["operation_key"] != second["operation_key"]
    assert second["history"][-1]["issued_record_correction_ref"] == "correction-route-B"
    assert not first["committed"] and not second["committed"]


def test_unchanged_issued_approval_requires_no_wording_correction():
    case = issued_case(changed=False)
    result = preview(**case)
    assert result["state"] == "APPROVED_PROPOSAL"
    assert result["after"]["wording"] == case["current"]["wording"]
    assert not result["committed"]


@pytest.mark.parametrize("disposition,state", [("hold", "HELD"), ("reject", "REJECTED_PROPOSAL")])
def test_hold_and_reject_preserve_issued_wording(disposition, state):
    case = issued_case(disposition)
    result = preview(**case)
    assert result["state"] == state
    assert result["after"]["wording"] == case["current"]["wording"]
    assert not result["committed"]
