"""Reproducible multi-forum contract tests: fictional sources only."""
import copy
from scripts.meeting_blueprints import compile_meeting_portfolio


def forum(ref, register):
    return {"forum_ref": ref, "profile_revision": "rev-1", "display_name": ref,
            "register_ref": register, "template_ref": "template-standard",
            "agenda_sections": ["standing", "new"], "control_keys": ["papers", "actions"],
            "capabilities": ["prepare", "compare_calendar"]}


def test_two_forums_share_templates_but_not_identity():
    source = [forum("medication", "decisions-register"), forum("quality", "decisions-register")]
    before = copy.deepcopy(source)
    result = compile_meeting_portfolio(source)
    assert result["state"] == "review_only"
    assert len(result["forums"]) == 2
    assert result["forums"][0]["namespace"] != result["forums"][1]["namespace"]
    assert {x["register_ref"] for x in result["forums"]} == {"decisions-register"}
    assert source == before
    assert compile_meeting_portfolio(list(reversed(source)))["sha256"] == result["sha256"]


def test_duplicate_forum_and_invalid_revision_refused():
    assert compile_meeting_portfolio([forum("quality", "r"), forum("quality", "r")])["state"] == "blocked"
    f = forum("quality", "r")
    f["profile_revision"] = ""
    assert compile_meeting_portfolio([f])["state"] == "blocked"


def test_premium_and_unknown_bindings_refused():
    f = forum("quality", "r")
    f["capabilities"].append("copilot")
    assert compile_meeting_portfolio([f])["state"] == "blocked"
    f = forum("quality", "r")
    f["native_binding"] = "example"
    assert compile_meeting_portfolio([f])["state"] == "blocked"


def test_configuration_never_issues_decisions_or_tasks():
    result = compile_meeting_portfolio([forum("quality", "r")])
    assert result["forums"][0]["automations"] == ["preflight", "carry_forward_review", "calendar_compare"]
    assert result["forums"][0]["create_actions"] is False
    assert result["forums"][0]["issue_minutes"] is False
    assert result["native_write_authorised"] is False
    assert result["premium_required"] is False and result["copilot_required"] is False
    assert result["core_connectors"] == ["sharepoint", "office365_outlook", "planner_basic_optional"]
