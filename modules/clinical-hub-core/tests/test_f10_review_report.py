from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.f10_review_report import _render_f10_test_catalog, render_pinned_f10_rev4_test_catalog


def _case(case_id, lane, status, *, record_id="FICTIONAL-A1", reasons="", reviewed="fictional-v7"):
    return {
        "case_id": case_id,
        "lane": lane,
        "reasons": reasons,
        "source_snapshot": {
            "case_id": case_id,
            "source_id": "FICTIONAL-SOURCE-1",
            "snapshot_version": "fictional-v7",
            "reviewed_version": reviewed,
            "snapshot_time": "2099-01-01T09:00:00+10:00",
            "record_id": record_id,
            "source_text": "Fictional source text must not appear in the report.",
            "status": status,
            "commissioned_claim": True,
            "issued_claim": True,
            "owner_claim": "FICTIONAL ROLE",
            "review_date": "2099-02-01",
            "due_date": None,
            "closure_acceptance": None,
            "closure_evidence_ref": None,
            "meeting_confirmed_claim": True,
            "duplicate_claim": False,
            "conflict_claim": False,
            "history": ["fictional-open-v6"],
            "response_ref": None,
        },
        "claims_status": "UNVERIFIED_FICTIONAL_INPUT",
        "selected_for_agenda": False,
        "issued": False,
        "assigned": False,
        "notified": False,
        "committed": False,
        "closed": False,
    }


def _result():
    cases = [
        _case("valid_issued", "PROPOSED_REVIEW", "open"),
        _case("pending_closure", "PROPOSED_REVIEW", "closure_pending", reasons="CLOSURE_PENDING;"),
        _case("held_case", "EXCLUDED_REVIEW", "held", record_id="FICTIONAL-A3", reasons="HELD;"),
        _case("stale_case", "BLOCKING_EXCEPTION", "open", record_id="FICTIONAL-A2",
              reasons="STALE_VERSION;", reviewed="fictional-v6"),
    ]
    result = {
        "status": "PROPOSAL_ONLY",
        "claims_status": "UNVERIFIED_FICTIONAL_INPUT",
        "meeting": "fictional occurrence; no actual meeting identity verified",
        "source": "fixed fictional snapshot; no live register read",
        "all_cases": cases,
        "proposed_review": [deepcopy(row) for row in cases if row["lane"] == "PROPOSED_REVIEW"],
        "excluded_review": [deepcopy(row) for row in cases if row["lane"] == "EXCLUDED_REVIEW"],
        "blocking_exceptions": [deepcopy(row) for row in cases if row["lane"] == "BLOCKING_EXCEPTION"],
        "chair_selection_required": True,
        "agenda_updated": False,
        "register_updated": False,
        "planner_updated": False,
        "notified": False,
    }
    return result


def test_render_is_explicitly_a_scenario_catalog_not_a_worklist():
    result = _result()
    original = deepcopy(result)

    report = _render_f10_test_catalog(result)

    assert report.startswith("# FICTIONAL TEST CATALOG - NOT A WORKLIST / NOT FOR ACTION")
    assert "4 alternative test scenarios" in report
    assert "2 proposed for human review; not selected" in report
    assert "1 excluded from the proposed review" in report
    assert "1 blocked for manual reconciliation" in report
    assert "not simultaneous actions or one coherent snapshot" in report
    assert "**Repeated fictional record IDs:** FICTIONAL-A1." in report
    assert "## Scenario `valid_issued`" in report and "## Scenario `pending_closure`" in report
    assert report.count("`FICTIONAL-SOURCE-1` / `FICTIONAL-A1`") == 2
    assert "fictional-v7 / fictional-v6 (mismatch)" in report
    assert "CLOSURE_PENDING: reported complete but closure acceptance remains pending" in report
    assert "STALE_VERSION" in report
    assert "Report effects: no selection or issue was produced by this report; no assignment, notification, commit, or closure. Source claims remain unverified." in report
    assert "no agenda, register, or Planner update; no notification" in report
    assert "existing manual source-linked review" in report
    assert "Fictional source text must not appear" not in report
    assert result == original


@pytest.mark.parametrize("mutate, message", [
    (lambda data: data.update(register_updated=True), "Top-level external-effect flag"),
    (lambda data: data["all_cases"][0].update(issued=True), "Effect flag is true"),
    (lambda data: (data["all_cases"][1].update(case_id="valid_issued"),
                   data["all_cases"][1]["source_snapshot"].update(case_id="valid_issued")),
     "Scenario case IDs must be unique"),
    (lambda data: data["all_cases"][0]["source_snapshot"].update(record_id="A1"), "Non-fictional source or record ID"),
    (lambda data: data["all_cases"][0]["source_snapshot"].update(snapshot_time="2099-01-01T09:00:00"), "canonical snapshot time"),
    (lambda data: data["all_cases"][0].update(lane="SELECTED"), "Unknown review lane"),
    (lambda data: data["proposed_review"].pop(), "does not match the full scenario rows"),
])
def test_rejects_effectful_malformed_or_inconsistent_input(mutate, message):
    result = _result()
    mutate(result)

    with pytest.raises(ValueError, match=message):
        _render_f10_test_catalog(result)


def test_rejects_unknown_schema_instead_of_silently_dropping_fields():
    result = _result()
    result["unexpected"] = "new output field"

    with pytest.raises(ValueError, match="unexpected top-level shape"):
        _render_f10_test_catalog(result)


@pytest.mark.parametrize("timestamp", ["2099-01-01|09:00:00+10:00", "2099-01-01\n09:00:00+10:00"])
def test_rejects_markdown_injection_in_snapshot_time(timestamp):
    result = _result()
    result["all_cases"][0]["source_snapshot"]["snapshot_time"] = timestamp

    with pytest.raises(ValueError, match="canonical snapshot time"):
        _render_f10_test_catalog(result)


def test_rejects_group_summary_that_changes_a_case_field():
    result = _result()
    result["proposed_review"][0]["reasons"] = "ALTERED;"

    with pytest.raises(ValueError, match="does not match the full scenario rows"):
        _render_f10_test_catalog(result)


def test_pinned_renderer_rejects_unverified_or_altered_native_payload():
    with pytest.raises(ValueError, match="original JSON bytes"):
        render_pinned_f10_rev4_test_catalog("{}")
    with pytest.raises(ValueError, match="digest differs"):
        render_pinned_f10_rev4_test_catalog(b"{}")
