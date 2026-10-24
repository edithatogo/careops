import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
import pytest


MODULE = Path(__file__).parents[1] / "scripts/validate_f15_flow_package.py"
spec = importlib.util.spec_from_file_location("validate_f15_flow_package", MODULE)
validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate)


PACKAGE_RESOURCE_ID = validate.PACKAGE_RESOURCE_ID


def package_file(tmp_path, date_expression="@if(not(contains(createArray('known', 'unknown', 'ambiguous'), item()?['response_date_state'])), 'RESPONSE_DATE_STATE_UNKNOWN', if(equals(item()?['response_date_state'], 'unknown'), 'RESPONSE_DATE_UNKNOWN', if(equals(item()?['response_date_state'], 'ambiguous'), 'RESPONSE_DATE_AMBIGUOUS', if(empty(item()?['response_date_value']), 'RESPONSE_DATE_VALUE_MISSING', 'RESPONSE_DATE_CLAIM_UNVERIFIED'))))"):
    cases = [
        ("TEST-REFERRAL-NO-RESPONSE", "open", "referred", "", False, "unanswered", "unknown", None),
        ("TEST-TASK-COMPLETE", "open", "closed", "", True, "complete", "known", "2026-09-01"),
        ("TEST-DISPUTED-CLOSURE", "closure_pending", "closed", "TEST-RESPONSE-3", True, "disputed", "known", "2026-09-02"),
        ("TEST-REOPENED", "closed", "reopened", "TEST-RESPONSE-4", False, "withdrawn", "ambiguous", None),
        ("TEST-PARTIAL-RESPONSE", "referred", "returned", "TEST-PARTIAL-5", False, "partial", "known", "2026-09-03"),
        ("TEST-BLANK-DATE", "held", "held", "", False, "complete", "unknown", None),
        ("TEST-DELAYED-RESPONSE", "referred", "returned", "TEST-RESPONSE-7", False, "delayed", "known", "2026-09-04"),
        ("TEST-COMPLETE-RESPONSE-CONTROL", "referred", "returned", "TEST-RESPONSE-8", False, "complete", "known", "2026-09-05"),
        ("TEST-UNKNOWN-RESPONSE-STATE", "referred", "returned", "TEST-RESPONSE-9", False, "unclassified", "known", "2026-09-06"),
    ]
    cases = [{
        "case_id": case_id, "prior_state": prior, "proposed_state": proposed,
        "source_ref": f"TEST-MIN-1#P{index}", "source_revision": "TEST-REV-1",
        "response_ref": response_ref, "reported_complete": completed,
        "closure_acceptance": "disputed" if case_id == "TEST-DISPUTED-CLOSURE" else "withdrawn" if case_id == "TEST-REOPENED" else "none",
        "disputed": case_id == "TEST-DISPUTED-CLOSURE", "reopen_reason": "TEST-NEW-EVIDENCE" if case_id == "TEST-REOPENED" else "",
        "response_state": response_state, "response_date_state": date_state, "response_date_value": date_value,
    } for index, (case_id, prior, proposed, response_ref, completed, response_state, date_state, date_value) in enumerate(cases, 1)]
    select = {
        "case_id": "@item()?['case_id']",
        "label": "FICTIONAL TEST — PROPOSED REVIEW ONLY",
        "prior_state": "@item()?['prior_state']",
        "proposed_state": "@item()?['proposed_state']",
        "source_reference_review_code": "@if(empty(item()?['source_ref']), 'SOURCE_REFERENCE_MISSING', if(empty(item()?['source_revision']), 'SOURCE_REVISION_MISSING', 'SOURCE_REFERENCES_UNVERIFIED'))",
        "response_review_code": "@if(equals(item()?['response_state'], 'unanswered'), 'NO_RESPONSE', if(not(contains(createArray('complete', 'partial', 'disputed', 'withdrawn', 'delayed', 'unanswered'), item()?['response_state'])), 'RESPONSE_STATE_UNKNOWN', if(equals(item()?['response_state'], 'complete'), 'RESPONSE_CLAIM_UNVERIFIED', if(equals(item()?['response_state'], 'partial'), 'PARTIAL_RESPONSE_REQUIRES_REVIEW', if(equals(item()?['response_state'], 'disputed'), 'DISPUTED_RESPONSE_REQUIRES_REVIEW', if(equals(item()?['response_state'], 'withdrawn'), 'WITHDRAWN_RESPONSE_REQUIRES_REVIEW', 'DELAYED_RESPONSE_REQUIRES_REVIEW'))))))",
        "response_review_reason": "@if(equals(item()?['response_state'], 'unanswered'), 'No response is included in this fictional test case; human review is required.', if(not(contains(createArray('complete', 'partial', 'disputed', 'withdrawn', 'delayed', 'unanswered'), item()?['response_state'])), 'Response state is not classified; human review is required.', if(equals(item()?['response_state'], 'complete'), 'Completion is reported; response sufficiency remains unverified.', if(equals(item()?['response_state'], 'partial'), 'Response is marked partial and needs human review.', if(equals(item()?['response_state'], 'disputed'), 'Response is disputed and needs human review.', if(equals(item()?['response_state'], 'withdrawn'), 'Response is withdrawn and needs human review.', 'Response is delayed and needs human review.'))))))",
        "response_date_review_code": date_expression,
        "response_date_review_reason": "@if(equals(item()?['response_date_state'], 'unknown'), 'No response date was supplied; its state is unknown.', if(equals(item()?['response_date_state'], 'ambiguous'), 'The response date is ambiguous and needs human review.', if(empty(item()?['response_date_value']), 'No date value was supplied for a known date state.', 'The supplied response date is unverified.')))" ,
        "closure_review_code": "@if(equals(item()?['proposed_state'], 'closed'), if(equals(item()?['closure_acceptance'], 'accepted'), 'CLOSURE_CLAIM_UNVERIFIED', 'CLOSURE_NOT_ACCEPTED'), 'NOT_PROPOSED_CLOSED')",
        "reopen_review_code": "@if(equals(item()?['proposed_state'], 'reopened'), 'REOPEN_CLAIM_UNVERIFIED', 'NOT_REOPENED')",
        "reported_complete_claim": "@item()?['reported_complete']",
        "result": "PROPOSED_FOR_HUMAN_REVIEW",
        "human_disposition": None,
        "human_disposition_required": True,
        "closure_accepted": False,
        "register_write_performed": False,
        "notification_sent": False,
    }
    definition = {
        "triggers": {"manual": {"type": "Request", "kind": "Button", "inputs": {"schema": {"properties": {}, "additionalProperties": False}}}},
        "actions": {
            "Fixed_Fictional_Cases": {"type": "Compose", "runAfter": {}, "inputs": cases},
            "Proposed_Reviews": {"type": "Select", "runAfter": {"Fixed_Fictional_Cases": ["Succeeded"]}, "inputs": {"from": "@outputs('Fixed_Fictional_Cases')", "select": select}},
        },
        "connectionReferences": {},
    }
    path = tmp_path / "candidate.zip"
    asset = f"Microsoft.Flow/flows/{validate.PACKAGE_RESOURCE_ID}"
    flow_resource = {
        "name": validate.TARGET_FLOW_ID,
        "id": f"/providers/Microsoft.Flow/flows/{validate.TARGET_FLOW_ID}",
        "type": "Microsoft.Flow/flows",
        "properties": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_logicflows",
            "displayName": validate.TARGET_FLOW_NAME,
            "definition": definition,
            "connectionReferences": {},
        },
    }
    with ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"resources": {PACKAGE_RESOURCE_ID: {"type": "Microsoft.Flow/flows", "suggestedCreationType": "Update", "creationType": "Existing, New, Update", "details": {"displayName": validate.TARGET_FLOW_NAME}}}}))
        archive.writestr("Microsoft.Flow/flows/manifest.json", json.dumps({"packageSchemaVersion": "1.0", "flowAssets": {"assetPaths": [PACKAGE_RESOURCE_ID]}}))
        archive.writestr(f"{asset}/definition.json", json.dumps(flow_resource))
        archive.writestr(f"{asset}/apisMap.json", "{}")
        archive.writestr(f"{asset}/connectionsMap.json", "{}")
    return path


@pytest.mark.parametrize("change", [
    {"suggestedCreationType": "New"},
    {"creationType": None},
    {"creationType": "Existing, New"},
])
def test_package_must_explicitly_target_update(tmp_path, change):
    path = package_file(tmp_path)
    altered = tmp_path / "not-update.zip"
    with ZipFile(path) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name == "manifest.json":
                manifest = json.loads(data)
                resource = next(iter(manifest["resources"].values()))
                for key, value in change.items():
                    if value is None:
                        resource.pop(key)
                    else:
                        resource[key] = value
                data = json.dumps(manifest).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="observed export Update setup"):
        validate.validate_package(altered)


def test_package_must_have_one_matching_flow_resource(tmp_path):
    path = package_file(tmp_path)
    altered = tmp_path / "wrong-resource.zip"
    with ZipFile(path) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name == "manifest.json":
                manifest = json.loads(data)
                resource = next(iter(manifest["resources"].values()))
                resource["type"] = "Microsoft.Other/resource"
                data = json.dumps(manifest).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="must identify a flow"):
        validate.validate_package(altered)


def test_package_resource_key_must_match_inner_asset_path(tmp_path):
    path = package_file(tmp_path)
    altered = tmp_path / "mismatched-asset.zip"
    with ZipFile(path) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name == "Microsoft.Flow/flows/manifest.json":
                data = json.dumps({"flowAssets": {"assetPaths": ["SYN-OTHER-ASSET"]}}).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="must match the inner flow asset path"):
        validate.validate_package(altered)


def test_package_rejects_multiple_resources(tmp_path):
    path = package_file(tmp_path)
    altered = tmp_path / "multiple-resources.zip"
    with ZipFile(path) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name == "manifest.json":
                manifest = json.loads(data)
                manifest["resources"]["00000000-0000-0000-0000-000000000002"] = dict(next(iter(manifest["resources"].values())))
                data = json.dumps(manifest).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="exactly one root package resource"):
        validate.validate_package(altered)


def test_package_requires_exact_live_target_identity(tmp_path):
    path = package_file(tmp_path)
    altered = tmp_path / "wrong-target.zip"
    with ZipFile(path) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name.endswith("/definition.json"):
                flow = json.loads(data)
                flow["id"] = "/providers/Microsoft.Flow/flows/00000000-0000-0000-0000-000000000000"
                data = json.dumps(flow).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="exact F15 target"):
        validate.validate_package(altered)






def test_expected_wdl_binding_rejects_different_definition(tmp_path):
    package = package_file(tmp_path)
    expected = tmp_path / "different-definition.json"
    expected.write_text(json.dumps({"properties": {"definition": {"triggers": {}}}}))
    with pytest.raises(ValueError, match="differs from the reviewed expected definition"):
        validate.validate_package(package, expected)


def test_evaluates_embedded_date_and_response_guards(tmp_path):
    result = validate.validate_package(package_file(tmp_path))
    assert result["case_count"] == 9
    by_id = {row["case_id"]: row for row in result["outputs"]}
    assert by_id["TEST-BLANK-DATE"]["response_date_review_code"] == "RESPONSE_DATE_UNKNOWN"
    assert by_id["TEST-REOPENED"]["response_date_review_code"] == "RESPONSE_DATE_AMBIGUOUS"
    assert by_id["TEST-PARTIAL-RESPONSE"]["response_review_code"] == "PARTIAL_RESPONSE_REQUIRES_REVIEW"
    assert by_id["TEST-DISPUTED-CLOSURE"]["response_review_code"] == "DISPUTED_RESPONSE_REQUIRES_REVIEW"
    assert by_id["TEST-DELAYED-RESPONSE"]["response_review_code"] == "DELAYED_RESPONSE_REQUIRES_REVIEW"
    assert by_id["TEST-REOPENED"]["response_review_code"] == "WITHDRAWN_RESPONSE_REQUIRES_REVIEW"
    assert "partial" in by_id["TEST-PARTIAL-RESPONSE"]["response_review_reason"].lower()
    assert "disputed" in by_id["TEST-DISPUTED-CLOSURE"]["response_review_reason"].lower()
    assert "delayed" in by_id["TEST-DELAYED-RESPONSE"]["response_review_reason"].lower()
    assert "withdrawn" in by_id["TEST-REOPENED"]["response_review_reason"].lower()
    assert by_id["TEST-UNKNOWN-RESPONSE-STATE"]["response_review_code"] == "RESPONSE_STATE_UNKNOWN"
    assert all(row["result"] == "PROPOSED_FOR_HUMAN_REVIEW" for row in result["outputs"])
    assert all(row["human_disposition_required"] is True for row in result["outputs"])


def test_connector_or_write_capability_is_rejected(tmp_path):
    path = package_file(tmp_path)
    replacement = tmp_path / "with-connector.zip"
    with ZipFile(path) as original, ZipFile(replacement, "w") as archive:
        for name in original.namelist():
            data = original.read(name)
            if name.endswith("connectionsMap.json"):
                data = b'{"shared_sharepointonline": {}}'
            archive.writestr(name, data)
    try:
        validate.validate_package(replacement)
    except ValueError as exc:
        assert "connector-free" in str(exc)
    else:
        raise AssertionError("connector mapping was accepted")


def test_blank_date_case_cannot_fall_through_to_generic_response_route(tmp_path):
    path = package_file(tmp_path, date_expression="@if(equals(item()?['response_date_state'], 'unknown'), 'RESPONSE_DATE_CLAIM_UNVERIFIED', 'CHECKED')")
    try:
        validate.validate_package(path)
    except ValueError as exc:
        assert "Named regression route changed" in str(exc)
    else:
        raise AssertionError("blank historical date mismatch was not detected")




def test_duplicate_fixture_ids_and_unsafe_fields_are_rejected(tmp_path):
    original = package_file(tmp_path)
    altered = tmp_path / "duplicate.zip"
    with ZipFile(original) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name.endswith("definition.json"):
                flow_resource = json.loads(data)
                definition = flow_resource["properties"]["definition"]
                cases = definition["actions"]["Fixed_Fictional_Cases"]["inputs"]
                cases[-1]["case_id"] = cases[0]["case_id"]
                cases[-1]["unexpected"] = "synthetic narrative"
                data = json.dumps(flow_resource).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="bounded fixture schema"):
        validate.validate_package(altered)


def test_human_review_cannot_be_disabled_and_unexpected_output_is_rejected(tmp_path):
    original = package_file(tmp_path)
    altered = tmp_path / "no-human-review.zip"
    with ZipFile(original) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name.endswith("definition.json"):
                flow_resource = json.loads(data)
                definition = flow_resource["properties"]["definition"]
                select = definition["actions"]["Proposed_Reviews"]["inputs"]["select"]
                select["human_disposition_required"] = False
                data = json.dumps(flow_resource).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="Human disposition must remain required"):
        validate.validate_package(altered)


def test_output_cannot_echo_reference_in_label_or_boolean_field(tmp_path):
    original = package_file(tmp_path)
    altered = tmp_path / "echo-reference.zip"
    with ZipFile(original) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name.endswith("definition.json"):
                flow_resource = json.loads(data)
                definition = flow_resource["properties"]["definition"]
                select = definition["actions"]["Proposed_Reviews"]["inputs"]["select"]
                select["label"] = "@item()?['source_ref']"
                data = json.dumps(flow_resource).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="fixed fictional notice"):
        validate.validate_package(altered)


@pytest.mark.parametrize("reason_field", ["response_review_reason", "response_date_review_reason"])
def test_reason_fields_cannot_echo_source_references(tmp_path, reason_field):
    original = package_file(tmp_path)
    altered = tmp_path / f"echo-{reason_field}.zip"
    with ZipFile(original) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name.endswith("definition.json"):
                flow_resource = json.loads(data)
                definition = flow_resource["properties"]["definition"]
                select = definition["actions"]["Proposed_Reviews"]["inputs"]["select"]
                select[reason_field] = "@item()?['source_ref']"
                data = json.dumps(flow_resource).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="fixed state-specific text"):
        validate.validate_package(altered)


def test_invalid_calendar_date_is_rejected(tmp_path):
    original = package_file(tmp_path)
    altered = tmp_path / "invalid-date.zip"
    with ZipFile(original) as source, ZipFile(altered, "w") as target:
        for name in source.namelist():
            data = source.read(name)
            if name.endswith("definition.json"):
                flow_resource = json.loads(data)
                definition = flow_resource["properties"]["definition"]
                cases = definition["actions"]["Fixed_Fictional_Cases"]["inputs"]
                cases[1]["response_date_value"] = "2026-02-30"
                data = json.dumps(flow_resource).encode()
            target.writestr(name, data)
    with pytest.raises(ValueError, match="valid ISO calendar dates"):
        validate.validate_package(altered)
