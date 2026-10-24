from copy import deepcopy
import ast
from pathlib import Path

import pytest

from scripts.meeting_candidate_contract import validate_candidate_fixture


def fixture():
    meeting = {"meeting_ref": "fx-t74nfcdols", "occurrence_ref": "fx-f7b6dh5sd6", "status": "confirmed_fixture"}
    transcript = {
        "artifact_ref": "fx-s2zfqxr74u",
        "meeting_ref": meeting["meeting_ref"],
        "occurrence_ref": meeting["occurrence_ref"],
        "revision": "fx-yo7rawtd35",
        "content_hash": "fx-jdemeq7qz2",
        "metadata_state": "fixture_metadata_consistent",
    }
    passage = {
        "passage_ref": "fx-2u6j35ge2d",
        "meeting_ref": meeting["meeting_ref"],
        "occurrence_ref": meeting["occurrence_ref"],
        "transcript_artifact_ref": transcript["artifact_ref"],
        "transcript_revision": transcript["revision"],
        "transcript_hash": transcript["content_hash"],
        "start_ms": 100,
        "end_ms": 500,
        "status": "fixture_present",
    }
    candidate = {
        "candidate_ref": "fx-abu3xoma5m",
        "category": "proposed_action",
        "source_spans": [{"passage_ref": passage["passage_ref"], "start_ms": 120, "end_ms": 300}],
        "speaker_state": "ambiguous",
        "authority_state": "unverified",
        "markers": ["condition", "dissent"],
        "review_disposition": "held",
        "supersedes_candidate_ref": None,
    }
    return {
        "meeting": meeting,
        "audience_revision": "fx-v2564jd4l7",
        "transcript": transcript,
        "passages": [passage],
        "required_candidate_passage_refs": [passage["passage_ref"]],
        "candidate_set": {
            "artifact_ref": "fx-gr7hofc2zz",
            "revision": "fx-3dtriycvh5",
            "meeting_ref": meeting["meeting_ref"],
            "occurrence_ref": meeting["occurrence_ref"],
            "audience_revision": "fx-v2564jd4l7",
            "source_refs": [transcript["artifact_ref"]],
            "supersedes_artifact_ref": None,
            "candidates": [candidate],
        },
        "prior_sets": [],
    }


def prior_set(case, artifact_ref, revision, dispositions, *, transcript_revision=None, transcript_hash=None):
    return {
        "artifact_ref": artifact_ref,
        "revision": revision,
        "meeting_ref": case["meeting"]["meeting_ref"],
        "occurrence_ref": case["meeting"]["occurrence_ref"],
        "audience_revision": case["audience_revision"],
        "transcript_artifact_ref": case["transcript"]["artifact_ref"],
        "transcript_revision": transcript_revision or case["transcript"]["revision"],
        "transcript_hash": transcript_hash or case["transcript"]["content_hash"],
        "candidate_dispositions": dispositions,
    }


def codes(result):
    return [issue["code"] for issue in result["issues"]]


def test_valid_fixture_is_structural_and_every_candidate_remains_unissued():
    case = fixture()
    original = deepcopy(case)
    result = validate_candidate_fixture(case)
    assert result["state"] == "fixture_metadata_consistent"
    assert "no semantic support" in result["meaning"]
    assert result["candidate_state"] == "unissued_proposal"
    assert result["owner_inferred"] is result["due_date_inferred"] is False
    assert result["authority_inferred"] is result["external_action_proposed"] is False
    assert case == original


@pytest.mark.parametrize("path,value", [
    (("meeting", "meeting_ref"), "fx-7bbl7p7mqp"),
    (("transcript", "revision"), "fx-v2564jd4l7"),
    (("transcript", "content_hash"), "fx-7rvxp5mdva"),
    (("candidate_set", "audience_revision"), "fx-7bbl7p7mqp"),
    (("transcript", "metadata_state"), "pending"),
])
def test_stale_or_cross_meeting_source_binding_blocks(path, value):
    case = fixture()
    target = case
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    assert "SOURCE_BINDING_INVALID" in codes(validate_candidate_fixture(case))


def test_missing_required_and_unsupported_candidate_refs_are_separate():
    case = fixture()
    case["required_candidate_passage_refs"].append("fx-7bbl7p7mqp")
    case["passages"].append({**case["passages"][0], "passage_ref": "fx-7bbl7p7mqp", "start_ms": 600, "end_ms": 700})
    case["candidate_set"]["candidates"][0]["source_spans"].append(
        {"passage_ref": "fx-7rvxp5mdva", "start_ms": 10, "end_ms": 20}
    )
    result = validate_candidate_fixture(case)
    assert "MISSING_REQUIRED_PASSAGE" in codes(result)
    assert "UNSUPPORTED_CANDIDATE_REF" in codes(result)
    assert result["structural_coverage"]["missing_required_passage_refs"] == ["fx-7bbl7p7mqp"]
    assert result["structural_coverage"]["unsupported_candidate_passage_refs"] == ["fx-7rvxp5mdva"]


def test_unknown_required_passage_is_malformed_source_binding():
    case = fixture()
    case["required_candidate_passage_refs"].append("fx-7bbl7p7mqp")
    assert "SOURCE_BINDING_INVALID" in codes(validate_candidate_fixture(case))


def test_out_of_range_span_blocks():
    case = fixture()
    case["candidate_set"]["candidates"][0]["source_spans"][0]["end_ms"] = 501
    assert "PASSAGE_REF_INVALID" in codes(validate_candidate_fixture(case))


@pytest.mark.parametrize("field,value", [
    ("category", []),
    ("speaker_state", {}),
    ("authority_state", ["none"]),
    ("review_disposition", {}),
    ("markers", [[]]),
])
def test_malformed_enum_shapes_fail_closed(field, value):
    case = fixture()
    case["candidate_set"]["candidates"][0][field] = value
    assert "CANDIDATE_SCHEMA_INVALID" in codes(validate_candidate_fixture(case))


@pytest.mark.parametrize("field", ["transcript_text", "raw_transcript", "prompt", "speakerName", "model_output"])
def test_content_and_unknown_fields_are_rejected_without_echo(field):
    case = fixture()
    case["transcript"][field] = "SYNTHETIC_SENTINEL"
    result = validate_candidate_fixture(case)
    assert codes(result) == ["CONTENT_FIELD_REJECTED"]
    assert "SYNTHETIC_SENTINEL" not in repr(result)


def test_unknown_owner_or_due_fields_are_rejected():
    case = fixture()
    case["candidate_set"]["candidates"][0]["owner"] = "fx-t74nfcdols"
    assert codes(validate_candidate_fixture(case)) == ["CONTENT_FIELD_REJECTED"]


def test_categories_and_uncertainty_are_explicit_and_item_linked():
    case = fixture()
    candidates = case["candidate_set"]["candidates"]
    refs = ["fx-2u6j35ge2d", "fx-7bbl7p7mqp", "fx-7rvxp5mdva", "fx-jdemeq7qz2", "fx-t74nfcdols", "fx-f7b6dh5sd6", "fx-v2564jd4l7"]
    for index, category in enumerate(("advice", "referral", "proposed_action", "candidate_decision", "dissent", "condition", "held_matter")):
        item = deepcopy(candidates[0])
        item["candidate_ref"] = refs[index]
        item["category"] = category
        item["markers"] = ["held" if category == "held_matter" else category] if category in {"dissent", "condition", "held_matter"} else []
        item["speaker_state"] = "unattributed"
        item["authority_state"] = "none"
        candidates.append(item) if index else None
    assert validate_candidate_fixture(case)["state"] == "fixture_metadata_consistent"


@pytest.mark.parametrize("category,markers", [
    ("condition", []),
    ("dissent", ["condition"]),
    ("held_matter", ["dissent"]),
])
def test_condition_dissent_and_held_categories_require_linked_marker(category, markers):
    case = fixture()
    item = case["candidate_set"]["candidates"][0]
    item["category"] = category
    item["markers"] = markers
    assert "CANDIDATE_SCHEMA_INVALID" in codes(validate_candidate_fixture(case))


def test_correction_uses_new_candidate_and_set_refs_and_preserves_prior_disposition():
    case = fixture()
    prior_candidate_ref = case["candidate_set"]["candidates"][0]["candidate_ref"]
    prior_set_ref = case["candidate_set"]["artifact_ref"]
    case["prior_sets"] = [prior_set(
        case, prior_set_ref, case["candidate_set"]["revision"], {prior_candidate_ref: "held"}
    )]
    case["candidate_set"]["artifact_ref"] = "fx-7bbl7p7mqp"
    case["candidate_set"]["revision"] = "fx-7rvxp5mdva"
    case["candidate_set"]["supersedes_artifact_ref"] = prior_set_ref
    replacement = deepcopy(case["candidate_set"]["candidates"][0])
    replacement["candidate_ref"] = "fx-jdemeq7qz2"
    replacement["review_disposition"] = "amended_candidate"
    replacement["supersedes_candidate_ref"] = prior_candidate_ref
    case["candidate_set"]["candidates"] = [replacement]
    original_history = deepcopy(case["prior_sets"])
    assert validate_candidate_fixture(case)["state"] == "fixture_metadata_consistent"
    assert case["prior_sets"] == original_history


def test_amended_item_must_supersede_candidate_from_named_prior_set():
    case = fixture()
    prior_candidate_ref = "fx-abu3xoma5m"
    case["prior_sets"] = [
        prior_set(case, "fx-gr7hofc2zz", "fx-3dtriycvh5", {prior_candidate_ref: "held"}),
        prior_set(case, "fx-7bbl7p7mqp", "fx-7rvxp5mdva", {}),
    ]
    case["candidate_set"]["supersedes_artifact_ref"] = "fx-7bbl7p7mqp"
    item = case["candidate_set"]["candidates"][0]
    item["candidate_ref"] = "fx-jdemeq7qz2"
    item["review_disposition"] = "amended_candidate"
    item["supersedes_candidate_ref"] = prior_candidate_ref
    assert "HISTORY_INVALID" in codes(validate_candidate_fixture(case))


def test_candidate_ref_cannot_appear_in_multiple_prior_sets():
    case = fixture()
    prior_candidate_ref = "fx-abu3xoma5m"
    case["prior_sets"] = [
        prior_set(case, "fx-gr7hofc2zz", "fx-3dtriycvh5", {prior_candidate_ref: "held"}),
        prior_set(case, "fx-7bbl7p7mqp", "fx-7rvxp5mdva", {prior_candidate_ref: "rejected_candidate"}),
    ]
    assert "HISTORY_INVALID" in codes(validate_candidate_fixture(case))


def test_source_amendment_invalidates_prior_review_and_requires_new_pending_candidate():
    case = fixture()
    old_candidate_ref = case["candidate_set"]["candidates"][0]["candidate_ref"]
    old_set = prior_set(
        case, "fx-gr7hofc2zz", "fx-3dtriycvh5", {old_candidate_ref: "held"}
    )
    case["prior_sets"] = [old_set]
    case["transcript"]["revision"] = "fx-7bbl7p7mqp"
    case["transcript"]["content_hash"] = "fx-7rvxp5mdva"
    for passage in case["passages"]:
        passage["transcript_revision"] = case["transcript"]["revision"]
        passage["transcript_hash"] = case["transcript"]["content_hash"]
    case["candidate_set"]["artifact_ref"] = "fx-jdemeq7qz2"
    case["candidate_set"]["revision"] = "fx-t74nfcdols"
    case["candidate_set"]["supersedes_artifact_ref"] = old_set["artifact_ref"]
    item = case["candidate_set"]["candidates"][0]
    item["candidate_ref"] = "fx-f7b6dh5sd6"
    item["supersedes_candidate_ref"] = old_candidate_ref
    item["review_disposition"] = "pending"
    result = validate_candidate_fixture(case)
    assert result["state"] == "fixture_metadata_consistent"
    assert result["invalidated_prior_set_refs"] == [old_set["artifact_ref"]]
    assert old_set["candidate_dispositions"][old_candidate_ref] == "held"


def test_stale_prior_set_cannot_be_kept_without_explicit_supersession():
    case = fixture()
    old_candidate_ref = case["candidate_set"]["candidates"][0]["candidate_ref"]
    old_set = prior_set(case, "fx-7bbl7p7mqp", "fx-3dtriycvh5", {old_candidate_ref: "held"})
    old_set["transcript_revision"] = "fx-7rvxp5mdva"
    case["prior_sets"] = [old_set]
    result = validate_candidate_fixture(case)
    assert "HISTORY_INVALID" in codes(result)
    assert result["invalidated_prior_set_refs"] == [old_set["artifact_ref"]]
    assert result["latest_prior_set_ref"] == old_set["artifact_ref"]
    assert "supersede the latest prior set" in result["manual_next_step"]


def test_current_source_prior_set_also_requires_explicit_latest_supersession():
    case = fixture()
    old_set = prior_set(case, "fx-7bbl7p7mqp", "fx-3dtriycvh5", {})
    case["prior_sets"] = [old_set]
    result = validate_candidate_fixture(case)
    assert "HISTORY_INVALID" in codes(result)
    assert result["latest_prior_set_ref"] == old_set["artifact_ref"]
    assert "explicitly supersede this set" in result["manual_next_step"]
    case["candidate_set"]["artifact_ref"] = "fx-7rvxp5mdva"
    case["candidate_set"]["revision"] = "fx-jdemeq7qz2"
    case["candidate_set"]["supersedes_artifact_ref"] = old_set["artifact_ref"]
    case["candidate_set"]["candidates"][0]["candidate_ref"] = "fx-jdemeq7qz2"
    case["candidate_set"]["candidates"][0]["review_disposition"] = "pending"
    assert validate_candidate_fixture(case)["state"] == "fixture_metadata_consistent"


def test_stale_prior_set_cannot_carry_forward_reviewed_disposition():
    case = fixture()
    old_candidate_ref = case["candidate_set"]["candidates"][0]["candidate_ref"]
    old_set = prior_set(case, "fx-gr7hofc2zz", "fx-3dtriycvh5", {old_candidate_ref: "held"})
    old_set["transcript_revision"] = "fx-7bbl7p7mqp"
    case["prior_sets"] = [old_set]
    case["candidate_set"]["supersedes_artifact_ref"] = old_set["artifact_ref"]
    item = case["candidate_set"]["candidates"][0]
    item["candidate_ref"] = "fx-f7b6dh5sd6"
    item["supersedes_candidate_ref"] = old_candidate_ref
    item["review_disposition"] = "amended_candidate"
    assert "HISTORY_INVALID" in codes(validate_candidate_fixture(case))


def test_reused_prior_candidate_and_current_set_refs_block():
    case = fixture()
    prior_ref = case["candidate_set"]["candidates"][0]["candidate_ref"]
    case["prior_sets"] = [prior_set(case, "fx-7bbl7p7mqp", "fx-7rvxp5mdva", {prior_ref: "held"})]
    assert "HISTORY_INVALID" in codes(validate_candidate_fixture(case))
    case["candidate_set"]["artifact_ref"] = case["transcript"]["artifact_ref"]
    result = validate_candidate_fixture(case)
    assert "HISTORY_INVALID" in codes(result)
    assert result["latest_prior_set_ref"] == "fx-7bbl7p7mqp"
    assert "explicitly supersede this set" in result["manual_next_step"]


def test_required_refs_must_be_unique_and_well_formed():
    case = fixture()
    ref = case["required_candidate_passage_refs"][0]
    case["required_candidate_passage_refs"] = [ref, ref]
    assert "SOURCE_BINDING_INVALID" in codes(validate_candidate_fixture(case))


def test_validator_import_graph_has_no_network_provider_or_storage_adapter():
    tree = ast.parse(Path("scripts/meeting_candidate_contract.py").read_text())
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    assert imports == ["__future__", "scripts.meeting_transcript_contract"]
