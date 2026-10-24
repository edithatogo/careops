import json
from copy import deepcopy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from preflight_pack import validate


@pytest.fixture
def pack():
    return json.loads((ROOT / "tests/fixtures/pack_preflight.json").read_text())


def test_reports_review_and_page_limit_exceptions(pack):
    result = validate(pack)
    assert result["meeting_id"] == "SYN-2026-09-28"
    assert result["ready_for_manual_review"] is False
    assert {(item["paper"], item["check"]) for item in result["exceptions"]} == {
        ("SYN-02", "review"), ("SYN-02", "length")
    }


def test_clean_pack_is_only_ready_for_manual_review(pack):
    pack["papers"][1].update(
        reviewed=True, reviewed_source="synthetic://report", reviewed_version="1", pages=2,
    )
    result = validate(pack)
    assert result["ready_for_manual_review"] is True
    assert result["exceptions"] == []


@pytest.mark.parametrize(("field", "current_value"), [
    ("source", "synthetic://replacement"),
    ("version", "2"),
])
def test_changed_source_or_version_invalidates_recorded_review(pack, field, current_value):
    pack["papers"][0][field] = current_value

    result = validate(pack)

    assert result["ready_for_manual_review"] is False
    exception = next(item for item in result["exceptions"] if item["paper"] == "SYN-01")
    assert exception["check"] == "review_binding"
    assert "synthetic://" not in json.dumps(exception)
    assert current_value not in json.dumps(exception)


def test_reviewed_paper_without_source_and_version_binding_fails_closed(pack):
    pack["papers"][1].update(reviewed=True, pages=2)

    result = validate(pack)

    assert result["ready_for_manual_review"] is False
    assert {item["check"] for item in result["exceptions"]} == {"review_binding"}


def test_duplicate_id_is_an_exception_not_a_silent_merge(pack):
    duplicate = deepcopy(pack["papers"][0])
    pack["papers"].append(duplicate)
    assert any(item["check"] == "duplicate_id" for item in validate(pack)["exceptions"])


def test_duplicate_source_link_is_flagged_without_exposing_link(pack):
    duplicate = deepcopy(pack["papers"][0])
    duplicate["id"] = "SYN-03"
    duplicate["source"] = "  synthetic://brief  "
    pack["papers"].append(duplicate)

    result = validate(pack)
    assert result["ready_for_manual_review"] is False
    assert {item["check"] for item in result["exceptions"] if item["paper"] == "SYN-03"} == {"duplicate_source"}
    assert "synthetic://brief" not in json.dumps(result["exceptions"])


def test_rejects_unagreed_input_fields(pack):
    pack["papers"][0]["owner"] = "Fictional person"
    with pytest.raises(ValueError, match="agreed fields"):
        validate(pack)
