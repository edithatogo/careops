"""Fictional compiler checks only; these never connect to a tenant or model."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.f14_candidate_flow import bind_schema, build


FIXTURES = Path(__file__).parent / "fixtures" / "f14"


@pytest.fixture
def inputs(tmp_path):
    source = json.loads((FIXTURES / "source.json").read_text())
    schema = json.loads((FIXTURES / "output.schema.json").read_text())
    bindings = {"prompt_id": "11111111-1111-4111-8111-111111111111",
                "configuration_id": "22222222-2222-4222-8222-222222222222",
                "connection_name": "fictional-dataverse-connection"}
    native = {"id": bindings["configuration_id"], "configuration": {
        "prompt": [{"type": "literal", "text": "Required JSON Schema: " + json.dumps(schema)}],
        "definitions": {"inputs": [{"id": "SourceJSON", "quickTestValue": json.dumps(source)}]}}}
    paths = [FIXTURES / "source.json", FIXTURES / "output.schema.json",
             tmp_path / "native.json", tmp_path / "bindings.json"]
    paths[2].write_text(json.dumps(native))
    paths[3].write_text(json.dumps(bindings))
    return source, schema, native, bindings, paths


def test_five_fresh_ids_and_schema_are_derived_from_binding(inputs):
    source, schema, _, _, _ = inputs
    assert bind_schema(schema, source) == schema
    candidates = schema["properties"]["candidate_set"]["properties"]["candidates"]
    assert candidates["minItems"] == candidates["maxItems"] == 5
    assert candidates["items"]["properties"]["candidate_ref"]["enum"] == source["binding"]["candidate_ref_slots"]
    assert len(schema["properties"]["coverage"]["items"]["properties"]["passage_ref"]["enum"]) == 7


@pytest.mark.parametrize("fault", ["duplicate", "reused_set", "reused_item", "pair_order"])
def test_refuses_reused_or_misordered_lineage(inputs, fault):
    source, schema, _, _, _ = inputs
    source = deepcopy(source)
    if fault == "duplicate":
        source["binding"]["candidate_ref_slots"][1] = source["binding"]["candidate_ref_slots"][0]
    elif fault == "reused_set":
        source["binding"]["candidate_set_ref"] = source["prior_set"]["artifact_ref"]
    elif fault == "reused_item":
        source["supersession_pairs"][0]["supersedes_candidate_ref"] = source["binding"]["candidate_ref_slots"][0]
    else:
        source["supersession_pairs"].reverse()
    with pytest.raises(ValueError, match="fresh candidate identities"):
        bind_schema(schema, source)


@pytest.mark.parametrize("fault", ["configuration", "schema", "sample", "binding"])
def test_refuses_native_or_binding_drift(inputs, fault):
    _, schema, native, bindings, paths = inputs
    if fault == "configuration":
        native["id"] = "stale-fictional-configuration"
    elif fault == "schema":
        changed = deepcopy(schema)
        changed["properties"]["candidate_set"]["properties"]["artifact_ref"]["const"] = "fx-stale-set"
        native["configuration"]["prompt"][0]["text"] = "Required JSON Schema: " + json.dumps(changed)
    elif fault == "sample":
        native["configuration"]["definitions"]["inputs"][0]["quickTestValue"] = "{}"
    else:
        bindings["unexpected"] = "refused"
    paths[2].write_text(json.dumps(native))
    paths[3].write_text(json.dumps(bindings))
    with pytest.raises(ValueError):
        build(*paths)


def test_compiles_stopped_guarded_model_and_model_skipping_recovery(inputs):
    _, _, _, bindings, paths = inputs
    payload = build(*paths)
    assert payload["properties"]["state"] == "Stopped"
    definition = payload["properties"]["definition"]
    actions = definition["actions"]
    mode = actions["Input_guard"]["actions"]["Mode_branch"]
    prediction = mode["actions"]["Run_own_F14_prompt"]
    assert prediction["inputs"]["parameters"]["recordId"] == bindings["prompt_id"]
    assert prediction["inputs"]["retryPolicy"] == {"type": "none"}
    assert mode["else"]["actions"]["Set_supplied_output"]["type"] == "SetVariable"
    processing = actions["Try_processing"]["actions"]
    assert '"pattern"' not in json.dumps(processing["Parse_candidate"]["inputs"]["schema"])
    assert processing["All_native_checks"]["inputs"].count("not(empty(trim(") == 5
    assert len(processing["All_native_checks"]["inputs"]) < 8192
    assert processing["Result"]["inputs"]["downstream_write_performed"] is False
    connector_actions = []

    def collect(value):
        if isinstance(value, dict):
            if value.get("type") == "OpenApiConnection":
                connector_actions.append(value)
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(definition)
    assert connector_actions == [prediction]
