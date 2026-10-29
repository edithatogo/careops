#!/usr/bin/env python3
"""Build a local Power Automate definition candidate for the fictional F14 R4 trial.

This generates a definition only. It never connects to Power Platform or deploys it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "private/working/f14-rims-route-20261022"
DEFAULT_BINDINGS = DEFAULT_DIR / "compiler-bindings.json"
CONNECTOR_ID = "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps"
DISPLAY_NAME = "Clinical Hub | F14 | Transcript candidates Test"


def read_json(path: Path) -> tuple[bytes, Any]:
    raw = path.read_bytes()
    return raw, json.loads(raw)


def to_power_automate_schema(node: Any) -> Any:
    """Translate JSON Schema const constraints to the manual schema enum form."""
    if isinstance(node, list):
        return [to_power_automate_schema(item) for item in node]
    if not isinstance(node, dict):
        return node
    if "patternProperties" in node or node.get("pattern") not in (None, r"\S"):
        raise ValueError("Unsupported native schema pattern requires an explicit expression guard")
    # Power Automate disallows pattern with connector actions. Nonblank summary
    # uses trim/empty below; support_quote must equal the exact source passage.
    result = {key: to_power_automate_schema(value) for key, value in node.items()
              if key not in {"$schema", "const", "pattern"}}
    if "const" in node:
        result["enum"] = [node["const"]]
    return result


def bind_schema(template: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    """Derive every identity enum from the selected fictional input, without string replacement."""
    schema = json.loads(json.dumps(template))
    binding = source["binding"]
    slots = binding["candidate_ref_slots"]
    pairs = source["supersession_pairs"]
    old_ids = [p["supersedes_candidate_ref"] for p in pairs]
    if (len(slots) != 5 or len(set(slots)) != 5 or len(pairs) != 5
            or [p["candidate_ref"] for p in pairs] != slots
            or len(set(old_ids)) != 5 or set(slots).intersection(old_ids)
            or binding["candidate_set_ref"] == source["prior_set"]["artifact_ref"]
            or binding["candidate_set_revision_ref"] == source["prior_set"]["revision"]):
        raise ValueError("Exactly five fresh candidate identities and ordered supersession pairs are required")
    if len(binding["passages"]) != 7 or len({p["passage_ref"] for p in binding["passages"]}) != 7:
        raise ValueError("Exactly seven distinct source passages are required")
    props = schema["properties"]
    for field in ("source_sha256", "source_revision", "meeting_ref", "occurrence_ref"):
        props[field] = {"const": binding[field]}
    candidate_set = props["candidate_set"]["properties"]
    for field, value in {
        "artifact_ref": binding["candidate_set_ref"],
        "revision": binding["candidate_set_revision_ref"],
        "supersedes_artifact_ref": source["prior_set"]["artifact_ref"],
    }.items():
        candidate_set[field] = {"const": value}
    candidates = candidate_set["candidates"]
    candidates["minItems"] = candidates["maxItems"] = 5
    row = candidates["items"]["properties"]
    row["candidate_ref"] = {"enum": binding["candidate_ref_slots"]}
    row["supersedes_candidate_ref"] = {"enum": [p["supersedes_candidate_ref"] for p in source["supersession_pairs"]]}
    passages = [p["passage_ref"] for p in binding["passages"]]
    row["source_spans"]["items"]["properties"]["passage_ref"] = {"enum": passages}
    coverage = props["coverage"]
    coverage["minItems"] = coverage["maxItems"] = 7
    coverage["items"]["properties"]["passage_ref"] = {"enum": passages}
    coverage["items"]["properties"]["candidate_refs"]["items"] = {"enum": binding["candidate_ref_slots"]}
    props["manual_route"]["properties"]["urgent_passage_refs"]["items"] = {"enum": passages}
    return schema


def action(kind: str, inputs: Any, after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return {"type": kind, "inputs": inputs, "runAfter": after or {}}


def compose(value: Any, after: str) -> dict[str, Any]:
    return action("Compose", value, {after: ["Succeeded"]})


def terminate(code: str, message: str) -> dict[str, Any]:
    return {"type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {"code": code, "message": message}}}


def build(input_path: Path, schema_path: Path, native_path: Path,
          bindings_path: Path = DEFAULT_BINDINGS) -> dict[str, Any]:
    input_raw, source = read_json(input_path)
    _, schema = read_json(schema_path)
    _, native = read_json(native_path)
    _, bindings = read_json(bindings_path)
    if set(bindings) != {"prompt_id", "configuration_id", "connection_name"} or any(
            not isinstance(value, str) or not value.strip() for value in bindings.values()):
        raise ValueError("Exact private prompt, configuration and connection bindings are required")
    if native.get("id") != bindings["configuration_id"]:
        raise ValueError("Pinned native configuration ID changed")
    if schema != bind_schema(schema, source):
        raise ValueError("Output schema identity/count contract differs from the authoritative input binding")
    configuration = native["configuration"]
    literal = configuration["prompt"][0]["text"]
    marker = "Required JSON Schema:"
    if marker not in literal:
        raise ValueError("Native prompt has no qualified embedded output schema")
    native_schema, _ = json.JSONDecoder().raw_decode(literal.split(marker, 1)[1].lstrip())
    if native_schema != schema:
        raise ValueError("Native prompt output schema differs from the flow schema; save and read back the corrected prompt first")
    sample = configuration["definitions"]["inputs"][0]
    if sample["id"] != "SourceJSON" or json.loads(sample["quickTestValue"]) != source:
        raise ValueError("Native prompt SourceJSON sample differs from the pinned flow input")
    binding = source["binding"]
    if binding["source_revision"] != 1 or not binding["source_sha256"]:
        raise ValueError("Pinned fictional source identity is incomplete")
    input_hash = hashlib.sha256(input_raw).hexdigest()
    expected_hash = "c6d35c6567e3d96374b626ca740abad4fc0ce76f1dbe23c45ce4893316bdf703"
    if input_hash != expected_hash:
        raise ValueError(f"input-r4.json drift: expected {expected_hash}, got {input_hash}")
    if len(binding["passages"]) != 7 or len(binding["candidate_ref_slots"]) != 5:
        raise ValueError("Pinned R4 passage or candidate-slot count changed")

    default_source = json.dumps(source, ensure_ascii=False, separators=(",", ":"))
    manual_schema = {
        "type": "object", "required": ["text", "text_1", "text_2"],
        "properties": {
            "text": {"type": "string", "title": "Mode", "enum": ["Extract", "Review existing"], "default": "Extract"},
            "text_1": {"type": "string", "title": "SourceJSON", "default": default_source},
            "text_2": {"type": "string", "title": "ExistingCandidateJSON", "default": ""},
        },
    }
    trigger_text_1 = "@triggerBody()?['text_1']"
    trigger_text_2 = "@triggerBody()?['text_2']"
    candidate_array = "body('Parse_candidate')?['candidate_set']?['candidates']"
    coverage_array = "body('Parse_candidate')?['coverage']"

    # Guards are intentionally fixed to the fictional R4 fixture. The JSON schema
    # enforces the complete field shape, constants, enums, null owner/date and
    # unissued status. These native expressions additionally enforce the oracle's
    # passage/category treatment, exact five-row set, lineage and urgent route.
    expected_refs = binding["candidate_ref_slots"][:5]
    prior_refs = [pair["supersedes_candidate_ref"] for pair in source["supersession_pairs"][:5]]
    passage_ids = [p["passage_ref"] for p in binding["passages"]]
    category_by_index = ["candidate_decision", "held_matter", "dissent", "proposed_action", "held_matter"]
    check_expressions: list[str] = [
        f"equals(length({candidate_array}),5)", f"equals(length({coverage_array}),7)",
        f"equals(body('Parse_candidate')?['source_sha256'],'{binding['source_sha256']}')",
        f"equals(body('Parse_candidate')?['source_revision'],{binding['source_revision']})",
        f"equals(body('Parse_candidate')?['meeting_ref'],'{binding['meeting_ref']}')",
        f"equals(body('Parse_candidate')?['occurrence_ref'],'{binding['occurrence_ref']}')",
        f"equals(body('Parse_candidate')?['candidate_set']?['artifact_ref'],'{binding['candidate_set_ref']}')",
        f"equals(body('Parse_candidate')?['candidate_set']?['revision'],'{binding['candidate_set_revision_ref']}')",
        f"equals(body('Parse_candidate')?['candidate_set']?['supersedes_artifact_ref'],'{source['prior_set']['artifact_ref']}')",
        "equals(body('Parse_candidate')?['manual_route']?['route'],'existing_human_notes_minutes_route')",
        "equals(body('Parse_candidate')?['manual_route']?['automatic_delivery'],false)",
        f"equals(string(body('Parse_candidate')?['manual_route']?['urgent_passage_refs']), '[\"{passage_ids[4]}\"]')",
        "equals(body('Parse_candidate')?['status'],'unissued_proposal')",
        "equals(body('Parse_candidate')?['requires_human_review'],true)",
    ]
    filter_actions: dict[str, Any] = {}
    # Per-row identity, exact source passage and lineage; quote must be drawn from
    # that passage. Combined with schema bounds, this stops extra/omitted rows.
    for i in range(5):
        row_filter = f"Candidate_{i + 1}_by_id"
        filter_actions[row_filter] = {"type": "Query", "inputs": {"from": "@" + candidate_array, "where": f"@equals(item()?['candidate_ref'],'{expected_refs[i]}')"}, "runAfter": {}}
        row = f"first(body('{row_filter}'))"
        passage = binding["passages"][i]
        cov_filter = f"Coverage_{i + 1}"
        filter_actions[cov_filter] = {"type": "Query", "inputs": {"from": "@" + coverage_array, "where": f"@equals(item()?['passage_ref'],'{passage['passage_ref']}')"}, "runAfter": {}}
        cov = f"first(body('{cov_filter}'))"
        check_expressions.extend([
            f"equals(length(body('{row_filter}')),1)",
            f"equals({row}?['category'],'{category_by_index[i]}')",
            f"not(empty(trim({row}?['summary_text'])))",
            f"equals({row}?['supersedes_candidate_ref'],'{prior_refs[i]}')",
            f"equals(length({row}?['source_spans']),1)",
            f"equals(first({row}?['source_spans'])?['passage_ref'],'{passage['passage_ref']}')",
            f"equals(first({row}?['source_spans'])?['start_ms'],{passage['start_ms']})",
            f"equals(first({row}?['source_spans'])?['end_ms'],{passage['end_ms']})",
            f"equals({row}?['support_quote'],'{passage['text'].replace(chr(39), chr(39) * 2)}')",
            f"equals(length(body('{cov_filter}')),1)",
            f"equals({cov}?['treatment'],'represented')",
            f"equals(string({cov}?['candidate_refs']), '[\"{expected_refs[i]}\"]')",
        ])
        if i == 0:
            check_expressions.append(f"contains({row}?['markers'],'condition')")
        if i == 1:
            check_expressions.extend([f"equals({row}?['authority_state'],'none')", f"equals({row}?['review_disposition'],'held')"])
        if i == 2:
            check_expressions.extend([f"equals({row}?['speaker_state'],'unattributed')", f"contains({row}?['markers'],'dissent')"])
        if i == 3:
            check_expressions.extend([f"equals({row}?['owner'],null)", f"equals({row}?['due_date'],null)", f"equals({row}?['issued'],false)"])
    for i, treatment in ((5, "quoted_untrusted_instruction"), (6, "no_candidate")):
        p = binding["passages"][i]
        covname = f"Coverage_{i + 1}"
        filter_actions[covname] = {"type": "Query", "inputs": {"from": "@" + coverage_array, "where": f"@equals(item()?['passage_ref'],'{p['passage_ref']}')"}, "runAfter": {}}
        cov = f"first(body('{covname}'))"
        rowname = f"No_candidate_{i + 1}"
        filter_actions[rowname] = {"type": "Query", "inputs": {"from": "@" + candidate_array, "where": f"@contains(string(item()?['source_spans']),'{p['passage_ref']}')"}, "runAfter": {}}
        check_expressions.extend([
            f"equals(length(body('{covname}')),1)",
            f"equals({cov}?['treatment'],'{treatment}')",
            f"equals(length({cov}?['candidate_refs']),0)",
            f"equals(length(body('{rowname}')),0)",
        ])

    actions: dict[str, Any] = {
        "Initialize_Candidate": {"type": "InitializeVariable", "inputs": {"variables": [{"name": "Candidate", "type": "string", "value": ""}]}, "runAfter": {}},
        "Input_guard": {
            "type": "If",
            "expression": {"and": [
                {"equals": [trigger_text_1, default_source]},
                {"or": [{"equals": ["@triggerBody()?['text']", "Extract"]}, {"equals": ["@triggerBody()?['text']", "Review existing"]}]},
            ]},
            "actions": {
                "Mode_branch": {
                    "type": "If", "expression": {"equals": ["@triggerBody()?['text']", "Extract"]},
                    "actions": {
                        "Run_own_F14_prompt": {
                            "type": "OpenApiConnection", "inputs": {"host": {"connectionName": "shared_commondataserviceforapps", "operationId": "aibuilderpredict_customprompt", "apiId": CONNECTOR_ID},
                                "parameters": {"recordId": bindings["prompt_id"], "item/requestv2/SourceJSON": trigger_text_1,
                                    "item/source": "@concat('{\"consumptionSource\":\"PowerAutomate\",\"partnerSource\":\"AIBuilder\",\"consumptionSourceVersion\":\"Flow\",\"partnerSourceVersion\":\"',workflow().name,'\"}')"},
                                "retryPolicy": {"type": "none"}},
                            "runAfter": {},
                        },
                        "Set_model_output": {"type": "SetVariable", "inputs": {"name": "Candidate", "value": "@body('Run_own_F14_prompt')?['responsev2']?['predictionOutput']?['text']"}, "runAfter": {"Run_own_F14_prompt": ["Succeeded"]}},
                    },
                    "else": {"actions": {"Set_supplied_output": {"type": "SetVariable", "inputs": {"name": "Candidate", "value": trigger_text_2}, "runAfter": {}}}},
                    "runAfter": {},
                },
            },
            "else": {"actions": {"Stop_unpinned_input": terminate("SOURCE_OR_MODE_MISMATCH", "Input must exactly match the pinned fictional R4 JSON and an allowed mode.")}},
            "runAfter": {"Initialize_Candidate": ["Succeeded"]},
        },
        "Try_processing": {"type": "Scope", "runAfter": {"Input_guard": ["Succeeded"]}, "actions": {
        "Parse_candidate": {"type": "ParseJson", "inputs": {"content": "@variables('Candidate')", "schema": to_power_automate_schema(schema)}, "runAfter": {}},
        **{name: {**value, "runAfter": {"Parse_candidate": ["Succeeded"]}} for name, value in filter_actions.items()},
        "All_native_checks": {**action("Compose", "@and(" + ",".join(check_expressions) + ")", {name: ["Succeeded"] for name in filter_actions}), "runAfter": {name: ["Succeeded"] for name in filter_actions}},
        "Native_contract_guard": {
            "type": "If", "expression": {"equals": ["@outputs('All_native_checks')", True]},
            "actions": {"Contract_pass": action("Compose", "PASS")},
            "else": {"actions": {"Stop_contract_mismatch": terminate("CANDIDATE_CONTRACT_HOLD", "Candidate output failed pinned R4 native structural guards; use manual review.")}},
            "runAfter": {"All_native_checks": ["Succeeded"]},
        },
        "Result": compose({
            "mode": "@if(equals(triggerBody()?['text'],'Extract'),'MODEL_EXTRACT_HUMAN_REVIEW_REQUIRED','UNVERIFIED_SUPPLIED_OUTPUT_NO_MODEL_EXECUTION')",
            "source_identity": {"source_revision": binding["source_revision"], "source_sha256": binding["source_sha256"], "transcript_artifact_ref": binding["transcript_artifact_ref"], "transcript_revision_ref": binding["transcript_revision_ref"], "transcript_hash_ref": binding["transcript_hash_ref"], "meeting_ref": binding["meeting_ref"], "occurrence_ref": binding["occurrence_ref"]},
            "candidate": "@body('Parse_candidate')",
            "human_review_required": True, "status": "unissued_proposal", "automatic_delivery": False,
            "downstream_write_performed": False,
            "notice": "Review aid only. No SharePoint, message, register, task, or file write; semantic correctness and urgent human follow-through require human review.",
        }, "Native_contract_guard"),
        }},
        "Manual_hold_on_failure": {
            "type": "Compose", "inputs": {"status": "MANUAL_HOLD", "source_identity": {"source_revision": binding["source_revision"], "source_sha256": binding["source_sha256"], "meeting_ref": binding["meeting_ref"], "occurrence_ref": binding["occurrence_ref"]}, "automatic_delivery": False, "downstream_write_performed": False, "manual_route": "existing_human_notes_minutes_route", "note": "Inspect failed, timed out, malformed, or contract-invalid processing and use the source through the existing manual route. No automatic model retry."},
            "runAfter": {"Try_processing": ["Failed", "TimedOut"]},
        },
        "Input_failure_hold": {
            "type": "Compose", "inputs": {"status": "MANUAL_HOLD", "source_identity": {"source_revision": binding["source_revision"], "source_sha256": binding["source_sha256"], "meeting_ref": binding["meeting_ref"], "occurrence_ref": binding["occurrence_ref"]}, "automatic_delivery": False, "downstream_write_performed": False, "manual_route": "existing_human_notes_minutes_route", "note": "Input validation or model branch failed or timed out. Inspect the original source through the existing manual route; no automatic model retry."},
            "runAfter": {"Input_guard": ["Failed", "TimedOut"]},
        },
    }
    # Catch model action errors at the branch boundary without retrying the model.
    mode_if = actions["Input_guard"]["actions"]["Mode_branch"]
    mode_if["else"]["actions"]["Set_supplied_output"]["runAfter"] = {}
    definition = {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {"$authentication": {"defaultValue": {}, "type": "SecureObject"}, "$connections": {"defaultValue": {}, "type": "Object"}},
        "triggers": {"manual": {"type": "Request", "kind": "Button", "inputs": {"schema": manual_schema}, "runtimeConfiguration": {"concurrency": {"runs": 1}}}},
        "actions": actions, "outputs": {},
    }
    # Ensure the exact referenced connector is declared; do not import RIMS refs or tier overrides.
    connections = {"shared_commondataserviceforapps": {"connectionName": bindings["connection_name"], "id": CONNECTOR_ID, "source": "Embedded"}}
    return {"properties": {"displayName": DISPLAY_NAME, "state": "Stopped", "definition": definition, "connectionReferences": connections}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_DIR / "input-r4.json")
    parser.add_argument("--schema", type=Path, default=DEFAULT_DIR / "output-r4.schema.json")
    parser.add_argument("--native-configuration", type=Path, default=DEFAULT_DIR / "native-configuration-r4.json")
    parser.add_argument("--bindings", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--output", type=Path, default=DEFAULT_DIR / "flow-candidate.json")
    args = parser.parse_args()
    body = build(args.input, args.schema, args.native_configuration, args.bindings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote local flow definition candidate: {args.output}")
    print("Pinned source input verified against its recorded SHA-256.")
    print("Not deployed or runtime-qualified; semantic review and parent-owned native runs remain outstanding.")


if __name__ == "__main__":
    main()
