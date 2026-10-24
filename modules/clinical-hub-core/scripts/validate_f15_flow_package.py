#!/usr/bin/env python3
"""Statically evaluate the bounded routing subset in an F15 Power Automate ZIP.

This checks the package's own expressions against its fixed cases. It is not a
Power Automate/WDL runtime and does not establish tenant behavior.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from zipfile import ZipFile


EXPR = re.compile(r"^@(if|equals|empty|not|contains|createArray|item|outputs)\(")
CASE_FIELDS = {
    "case_id", "prior_state", "proposed_state", "source_ref", "source_revision",
    "response_ref", "reported_complete", "closure_acceptance", "disputed",
    "reopen_reason", "response_state", "response_date_state", "response_date_value",
}
CASE_IDS = {
    "TEST-REFERRAL-NO-RESPONSE", "TEST-TASK-COMPLETE", "TEST-DISPUTED-CLOSURE",
    "TEST-REOPENED", "TEST-PARTIAL-RESPONSE", "TEST-BLANK-DATE",
    "TEST-DELAYED-RESPONSE", "TEST-COMPLETE-RESPONSE-CONTROL",
    "TEST-UNKNOWN-RESPONSE-STATE",
}
TARGET_FLOW_ID = "00000000-0000-4000-8000-000000000102"
TARGET_FLOW_NAME = "Clinical Directors - Fictional resolution review"
PACKAGE_RESOURCE_ID = "00000000-0000-4000-8000-000000000103"
OUTPUT_FIELDS = {
    "label", "case_id", "prior_state", "proposed_state", "source_reference_review_code",
    "response_review_code", "response_review_reason", "response_date_review_code",
    "response_date_review_reason", "closure_review_code",
    "reopen_review_code", "reported_complete_claim", "result", "human_disposition",
    "human_disposition_required", "closure_accepted", "register_write_performed",
    "notification_sent",
}
EXPECTED_ROUTES = {
    "TEST-REFERRAL-NO-RESPONSE": ("SOURCE_REFERENCES_UNVERIFIED", "NO_RESPONSE", "RESPONSE_DATE_UNKNOWN", "NOT_PROPOSED_CLOSED", "NOT_REOPENED"),
    "TEST-TASK-COMPLETE": ("SOURCE_REFERENCES_UNVERIFIED", "RESPONSE_CLAIM_UNVERIFIED", "RESPONSE_DATE_CLAIM_UNVERIFIED", "CLOSURE_NOT_ACCEPTED", "NOT_REOPENED"),
    "TEST-DISPUTED-CLOSURE": ("SOURCE_REFERENCES_UNVERIFIED", "DISPUTED_RESPONSE_REQUIRES_REVIEW", "RESPONSE_DATE_CLAIM_UNVERIFIED", "CLOSURE_NOT_ACCEPTED", "NOT_REOPENED"),
    "TEST-REOPENED": ("SOURCE_REFERENCES_UNVERIFIED", "WITHDRAWN_RESPONSE_REQUIRES_REVIEW", "RESPONSE_DATE_AMBIGUOUS", "NOT_PROPOSED_CLOSED", "REOPEN_CLAIM_UNVERIFIED"),
    "TEST-PARTIAL-RESPONSE": ("SOURCE_REFERENCES_UNVERIFIED", "PARTIAL_RESPONSE_REQUIRES_REVIEW", "RESPONSE_DATE_CLAIM_UNVERIFIED", "NOT_PROPOSED_CLOSED", "NOT_REOPENED"),
    "TEST-BLANK-DATE": ("SOURCE_REFERENCES_UNVERIFIED", "RESPONSE_CLAIM_UNVERIFIED", "RESPONSE_DATE_UNKNOWN", "NOT_PROPOSED_CLOSED", "NOT_REOPENED"),
    "TEST-DELAYED-RESPONSE": ("SOURCE_REFERENCES_UNVERIFIED", "DELAYED_RESPONSE_REQUIRES_REVIEW", "RESPONSE_DATE_CLAIM_UNVERIFIED", "NOT_PROPOSED_CLOSED", "NOT_REOPENED"),
    "TEST-COMPLETE-RESPONSE-CONTROL": ("SOURCE_REFERENCES_UNVERIFIED", "RESPONSE_CLAIM_UNVERIFIED", "RESPONSE_DATE_CLAIM_UNVERIFIED", "NOT_PROPOSED_CLOSED", "NOT_REOPENED"),
    "TEST-UNKNOWN-RESPONSE-STATE": ("SOURCE_REFERENCES_UNVERIFIED", "RESPONSE_STATE_UNKNOWN", "RESPONSE_DATE_CLAIM_UNVERIFIED", "NOT_PROPOSED_CLOSED", "NOT_REOPENED"),
}
RESPONSE_REASON_BY_STATE = {
    "unanswered": "No response is included in this fictional test case; human review is required.",
    "unclassified": "Response state is not classified; human review is required.",
    "complete": "Completion is reported; response sufficiency remains unverified.",
    "partial": "Response is marked partial and needs human review.",
    "disputed": "Response is disputed and needs human review.",
    "withdrawn": "Response is withdrawn and needs human review.",
    "delayed": "Response is delayed and needs human review.",
}
DATE_REASON_BY_STATE = {
    "unknown": "No response date was supplied; its state is unknown.",
    "ambiguous": "The response date is ambiguous and needs human review.",
    "known": "The supplied response date is unverified.",
}


def _split_args(source: str) -> list[str]:
    args: list[str] = []
    depth = 0
    quoted = False
    escaped = False
    start = 0
    for i, char in enumerate(source):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "'":
                quoted = False
        elif char == "'":
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(source[start:i].strip())
            start = i + 1
    args.append(source[start:].strip())
    return args


def _call(expression: str) -> tuple[str, list[str]]:
    match = EXPR.match(expression)
    if not match or not expression.endswith(")"):
        raise ValueError(f"Unsupported expression: {expression}")
    name = match.group(1)
    return name, _split_args(expression[match.end():-1])


def _literal_or_eval(source: str, item: dict[str, Any]) -> Any:
    source = source.strip()
    if source.startswith("'") and source.endswith("'"):
        return source[1:-1].replace("\\'", "'")
    if source == "null":
        return None
    if source == "true":
        return True
    if source == "false":
        return False
    if source.startswith("@"):
        return evaluate(source, item)
    if source.startswith("item()?['") and source.endswith("']"):
        return item.get(source[len("item()?['"):-2])
    if re.match(r"^(if|equals|empty|not|contains|createArray)\(", source):
        return evaluate("@" + source, item)
    raise ValueError(f"Unsupported expression value: {source}")


def evaluate(expression: str, item: dict[str, Any]) -> Any:
    """Evaluate only the pure expression functions used by the F15 candidate."""
    if expression == "@item()":
        return item
    if expression.startswith("@item()?['") and expression.endswith("']"):
        return item.get(expression[len("@item()?['"):-2])
    if not expression.startswith("@"):
        expression = "@" + expression
    name, args = _call(expression)
    if name == "item" and args == ["?"]:
        return item
    if name == "item" and len(args) == 1 and args[0].startswith("?['") and args[0].endswith("']"):
        return item.get(args[0][3:-2])
    if name == "if" and len(args) == 3:
        return _literal_or_eval(args[1], item) if _literal_or_eval(args[0], item) else _literal_or_eval(args[2], item)
    if name == "equals" and len(args) == 2:
        return _literal_or_eval(args[0], item) == _literal_or_eval(args[1], item)
    if name == "empty" and len(args) == 1:
        value = _literal_or_eval(args[0], item)
        return value is None or value == "" or value == [] or value == {}
    if name == "not" and len(args) == 1:
        return not _literal_or_eval(args[0], item)
    if name == "contains" and len(args) == 2:
        collection = _literal_or_eval(args[0], item)
        value = _literal_or_eval(args[1], item)
        return value in collection
    if name == "createArray":
        return [_literal_or_eval(arg, item) for arg in args]
    if name == "outputs" and len(args) == 1 and args[0] == "'Fixed_Fictional_Cases'":
        raise ValueError("outputs() is only valid as the Select source, not a field expression")
    raise ValueError(f"Unsupported function or arity: {name}/{len(args)}")


def load_package(path: Path) -> dict[str, Any]:
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        root_manifest = json.loads(archive.read("manifest.json"))
        resources = root_manifest.get("resources")
        if not isinstance(resources, dict) or len(resources) != 1:
            raise ValueError("Expected exactly one root package resource")
        resource_id, resource = next(iter(resources.items()))
        if not isinstance(resource, dict) or resource.get("type") != "Microsoft.Flow/flows":
            raise ValueError("Root package resource must identify a flow")
        if resource.get("creationType") != "Existing, New, Update" or resource.get("suggestedCreationType") != "Update":
            raise ValueError("Root package resource must preserve the observed export Update setup")
        details = resource.get("details")
        if not isinstance(details, dict) or details.get("displayName") != TARGET_FLOW_NAME:
            raise ValueError("Root package resource display name does not match F15")
        flow_manifests = [n for n in names if n.endswith("Microsoft.Flow/flows/manifest.json")]
        if len(flow_manifests) != 1:
            raise ValueError("Expected one Microsoft.Flow/flows/manifest.json")
        flow_manifest = json.loads(archive.read(flow_manifests[0]))
        paths = flow_manifest.get("flowAssets", {}).get("assetPaths", [])
        if len(paths) != 1 or not isinstance(paths[0], str) or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", paths[0]):
            raise ValueError("Expected one flow asset")
        if paths[0] != resource_id or resource_id != PACKAGE_RESOURCE_ID:
            raise ValueError("Root package resource ID must match the inner flow asset path")
        prefix = flow_manifests[0].rsplit("/", 1)[0]
        root = f"{prefix}/{paths[0]}"
        flow_resource = json.loads(archive.read(f"{root}/definition.json"))
        if flow_resource.get("id") != f"/providers/Microsoft.Flow/flows/{TARGET_FLOW_ID}" or flow_resource.get("name") != TARGET_FLOW_ID:
            raise ValueError("Nested flow definition does not identify the exact F15 target")
        if flow_resource.get("type") != "Microsoft.Flow/flows":
            raise ValueError("Nested definition must remain a flow resource")
        flow_properties = flow_resource.get("properties", {})
        if flow_properties.get("displayName") != TARGET_FLOW_NAME:
            raise ValueError("Nested flow display name does not match F15")
        if flow_properties.get("connectionReferences") not in ({}, None):
            raise ValueError("Candidate must remain connector-free")
        definition = flow_properties.get("definition")
        if not isinstance(definition, dict):
            raise ValueError("Nested flow definition is missing")
        apis = json.loads(archive.read(f"{root}/apisMap.json"))
        connections = json.loads(archive.read(f"{root}/connectionsMap.json"))
    return {"root_manifest": root_manifest, "flow_resource": flow_resource, "definition": definition, "apis": apis, "connections": connections}


def validate_package(path: Path, expected_wdl: Path | None = None) -> dict[str, Any]:
    package = load_package(path)
    definition = package["definition"]
    if expected_wdl is not None:
        expected_resource = json.loads(expected_wdl.read_text())
        expected_definition = expected_resource.get("properties", {}).get("definition")
        if definition != expected_definition:
            raise ValueError("Candidate WDL differs from the reviewed expected definition")
    triggers = definition.get("triggers", {})
    actions = definition.get("actions", {})
    if set(triggers) != {"manual"} or triggers["manual"].get("type") != "Request" or triggers["manual"].get("kind") != "Button":
        raise ValueError("Expected a single manual trigger")
    schema = triggers["manual"].get("inputs", {}).get("schema", {})
    if schema.get("properties") != {} or schema.get("additionalProperties") is not False:
        raise ValueError("Manual trigger must accept no input fields")
    if set(actions) != {"Fixed_Fictional_Cases", "Proposed_Reviews"}:
        raise ValueError("Unexpected action graph")
    if actions["Fixed_Fictional_Cases"].get("type") != "Compose" or actions["Proposed_Reviews"].get("type") != "Select":
        raise ValueError("Expected fixed Compose cases followed by Select")
    if actions["Fixed_Fictional_Cases"].get("runAfter") != {} or actions["Proposed_Reviews"].get("runAfter") != {"Fixed_Fictional_Cases": ["Succeeded"]}:
        raise ValueError("Unexpected action order or dependency")
    if package["apis"] or package["connections"] or package["definition"].get("connectionReferences"):
        raise ValueError("Candidate must remain connector-free")
    cases = actions["Fixed_Fictional_Cases"].get("inputs")
    selection = actions["Proposed_Reviews"].get("inputs", {})
    if not isinstance(cases, list) or len(cases) != 9:
        raise ValueError("Expected nine fixed fictional cases")
    if any(not isinstance(case, dict) or set(case) != CASE_FIELDS for case in cases):
        raise ValueError("Fixed case fields do not match the bounded fixture schema")
    case_ids = [case["case_id"] for case in cases]
    if len(set(case_ids)) != len(case_ids) or set(case_ids) != CASE_IDS:
        raise ValueError("Expected each named fictional case exactly once")
    for case in cases:
        if any(not isinstance(value, (str, bool, type(None))) for value in case.values()):
            raise ValueError("Fixture values must be bounded strings, booleans or null")
        if any(isinstance(value, str) and len(value) > 128 for value in case.values()):
            raise ValueError("Fixture string exceeds the 128-character bound")
        if not case["case_id"].startswith("TEST-"):
            raise ValueError("Fixture IDs must use the fictional TEST- prefix")
        if case["prior_state"] not in {"open", "closure_pending", "closed", "referred", "held"} or case["proposed_state"] not in {"closed", "reopened", "referred", "returned", "held"}:
            raise ValueError("Unexpected fixture disposition")
        if case["response_state"] not in {"unanswered", "complete", "disputed", "withdrawn", "partial", "delayed", "unclassified"}:
            raise ValueError("Unexpected fixture response state")
        if case["closure_acceptance"] not in {"none", "accepted", "disputed", "withdrawn"}:
            raise ValueError("Unexpected fixture closure claim")
        for ref_field in ("source_ref", "source_revision"):
            if not isinstance(case[ref_field], str) or not re.fullmatch(r"TEST-[A-Z0-9_-]{1,48}(?:#[A-Z0-9_-]{1,32})?", case[ref_field]):
                raise ValueError("Fixture source references must be synthetic TEST- values")
        if case["response_ref"] and not re.fullmatch(r"TEST-[A-Z0-9_-]{1,48}", case["response_ref"]):
            raise ValueError("Fixture response references must be synthetic TEST- values")
        if case["reopen_reason"] and not re.fullmatch(r"TEST-[A-Z0-9_-]{1,48}", case["reopen_reason"]):
            raise ValueError("Fixture reopen reasons must be synthetic TEST- values")
        if not isinstance(case["reported_complete"], bool) or not isinstance(case["disputed"], bool):
            raise ValueError("Reported completion and dispute flags must be booleans")
        if case["response_date_state"] not in {"known", "unknown", "ambiguous"}:
            raise ValueError("Unknown response date state")
        if case["response_date_state"] != "known" and case["response_date_value"] is not None:
            raise ValueError("Unknown or ambiguous dates must not carry a date value")
        if case["response_date_state"] == "known":
            try:
                if date.fromisoformat(case["response_date_value"]).isoformat() != case["response_date_value"]:
                    raise ValueError
            except (TypeError, ValueError):
                raise ValueError("Known fixture dates must be valid ISO calendar dates") from None
    select_map = selection.get("select", {})
    if selection.get("from") != "@outputs('Fixed_Fictional_Cases')":
        raise ValueError("Select must read only the fixed fictional cases")
    if set(select_map) != OUTPUT_FIELDS:
        raise ValueError("Select output fields do not match the allowlist")
    if select_map.get("human_disposition_required") is not True:
        raise ValueError("Human disposition must remain required")
    outputs = []
    for case in cases:
        result = {}
        for key, expression in select_map.items():
            if isinstance(expression, str) and expression.startswith("@"):
                if key == "result" or key == "human_disposition" or key in {
                    "human_disposition_required", "closure_accepted", "register_write_performed", "notification_sent"
                }:
                    continue
                result[key] = evaluate(expression, case)
            else:
                result[key] = expression
        expected = EXPECTED_ROUTES[case["case_id"]]
        if result.get("label") != "FICTIONAL TEST — PROPOSED REVIEW ONLY":
            raise ValueError("Output label must remain the fixed fictional notice")
        if result.get("case_id") != case["case_id"] or result.get("prior_state") != case["prior_state"] or result.get("proposed_state") != case["proposed_state"]:
            raise ValueError("Output may expose only the approved case and disposition fields")
        if result.get("reported_complete_claim") is not case["reported_complete"]:
            raise ValueError("Reported completion output must remain the supplied boolean")
        route_values = (
            result.get("source_reference_review_code"), result.get("response_review_code"),
            result.get("response_date_review_code"), result.get("closure_review_code"),
            result.get("reopen_review_code"),
        )
        if route_values != expected:
            raise ValueError(f"Named regression route changed for {case['case_id']}")
        expected_response_reason = RESPONSE_REASON_BY_STATE[case["response_state"]]
        expected_date_reason = DATE_REASON_BY_STATE[case["response_date_state"]]
        if result.get("response_review_reason") != expected_response_reason or len(expected_response_reason) > 128:
            raise ValueError("Response reason does not match the fixed state-specific text")
        if result.get("response_date_review_reason") != expected_date_reason or len(expected_date_reason) > 128:
            raise ValueError("Date reason does not match the fixed state-specific text")
        if any(not isinstance(value, (str, bool, type(None))) for value in result.values()):
            raise ValueError("Output contains an unsupported value type")
        if select_map.get("result") != "PROPOSED_FOR_HUMAN_REVIEW" or select_map.get("human_disposition") is not None:
            raise ValueError("Output must remain proposal-only with no human disposition")
        if select_map.get("closure_accepted") is not False or select_map.get("register_write_performed") is not False or select_map.get("notification_sent") is not False:
            raise ValueError("Output must not accept closure, write, or notify")
        outputs.append({"case_id": case.get("case_id"), **result})
    return {"case_count": len(cases), "outputs": outputs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--expected-wdl", type=Path, help="Flow export JSON whose properties.definition must match exactly")
    args = parser.parse_args()
    try:
        result = validate_package(args.package, args.expected_wdl)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
