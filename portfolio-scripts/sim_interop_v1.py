"""Validate a fictional, source-bound CareOps Sim run packet.

This adapter checks metadata only. It does not invoke the Rust engine, read
operational events, or persist or replace a simulation result.
"""

from __future__ import annotations

from datetime import date
import hashlib
import json
import re
from typing import Any
from pathlib import PurePosixPath


CONTRACT_VERSION = 1
SIM_SOURCE_COMMIT = "6ffd51392303cb08d249f71fbfdd8025771fcb55"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_packet(packet: dict[str, Any], *, as_of_date: date, input_files: dict[str, bytes]) -> dict[str, Any]:
    """Return deterministic validation metadata for a synthetic packet."""
    if type(packet.get("contractVersion")) is not int or packet.get("contractVersion") != CONTRACT_VERSION:
        return {"schemaVersion": CONTRACT_VERSION, "status": "IncompatibleVersion", "runs": []}
    if packet.get("providerAvailable") is not True:
        return {"schemaVersion": CONTRACT_VERSION, "status": "ProviderAbsent", "runs": []}

    observed = packet.get("observedDate")
    max_age = packet.get("maxAgeDays")
    try:
        observed_date = date.fromisoformat(observed)
    except (TypeError, ValueError):
        return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age < 0:
        return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}
    if (as_of_date - observed_date).days < 0 or (as_of_date - observed_date).days > max_age:
        return {"schemaVersion": CONTRACT_VERSION, "status": "Stale", "runs": []}

    source_commit = packet.get("engineSourceCommit")
    if source_commit != SIM_SOURCE_COMMIT:
        return {"schemaVersion": CONTRACT_VERSION, "status": "IncompatibleSource", "runs": []}
    run_documents = packet.get("runDocuments")
    if not isinstance(run_documents, list) or not run_documents:
        return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}

    by_identity: dict[str, dict[str, Any]] = {}
    for document in run_documents:
        if not isinstance(document, dict):
            return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}
        manifest = document.get("manifest")
        taxonomy = document.get("validation_taxonomy")
        summary = document.get("summary")
        if not isinstance(manifest, dict) or not isinstance(taxonomy, dict) or not isinstance(summary, dict):
            return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}

        schema_version = manifest.get("schema_version")
        if type(schema_version) is not int or schema_version != 1:
            return {"schemaVersion": CONTRACT_VERSION, "status": "IncompatibleVersion", "runs": []}
        scenario_id = manifest.get("scenario_id")
        input_file = manifest.get("input_file")
        input_sha256 = manifest.get("input_sha256")
        seed = manifest.get("seed")
        time_unit = manifest.get("time_unit")
        horizon = manifest.get("horizon_ticks")
        if (
            not isinstance(scenario_id, str) or not scenario_id.strip()
            or not isinstance(input_file, str) or not input_file.strip()
            or not isinstance(input_sha256, str) or not _SHA256.fullmatch(input_sha256)
            or not isinstance(seed, int) or isinstance(seed, bool) or seed < 0
            or not isinstance(time_unit, str) or not time_unit.strip()
            or not isinstance(horizon, int) or isinstance(horizon, bool) or horizon <= 0
        ):
            return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}
        safe_name = PurePosixPath(input_file)
        input_bytes = input_files.get(input_file)
        if safe_name.is_absolute() or ".." in safe_name.parts or input_bytes is None:
            return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}
        if hashlib.sha256(input_bytes).hexdigest() != input_sha256:
            return {"schemaVersion": CONTRACT_VERSION, "status": "InputDigestMismatch", "runs": []}
        try:
            scenario = json.loads(input_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"schemaVersion": CONTRACT_VERSION, "status": "MissingInput", "runs": []}
        if (
            not isinstance(scenario, dict)
            or type(scenario.get("schema_version")) is not int
            or not isinstance(scenario.get("provenance"), dict)
        ):
            return {"schemaVersion": CONTRACT_VERSION, "status": "InputManifestMismatch", "runs": []}
        if (
            scenario.get("schema_version") != schema_version
            or scenario.get("scenario_id") != scenario_id
            or scenario.get("seed") != seed
            or scenario.get("time_unit") != time_unit
            or scenario.get("horizon_ticks") != horizon
            or scenario["provenance"].get("class") != "synthetic"
        ):
            return {"schemaVersion": CONTRACT_VERSION, "status": "InputManifestMismatch", "runs": []}
        if taxonomy.get("verification_scope") != "software_verification" or taxonomy.get("validation_scope") != "none" or taxonomy.get("provenance_class") != "synthetic":
            return {"schemaVersion": CONTRACT_VERSION, "status": "UnsupportedProvenance", "runs": []}

        identity = _digest({"scenarioId": scenario_id, "seed": seed, "inputSha256": input_sha256})
        result = {
            "runId": identity,
            "scenarioId": scenario_id,
            "inputFile": input_file,
            "inputSha256": input_sha256,
            "seed": seed,
            "timeUnit": time_unit,
            "horizonTicks": horizon,
            "engineSourceCommit": SIM_SOURCE_COMMIT,
            "resultSha256": _digest(summary),
        }
        prior = by_identity.get(identity)
        if prior is not None and prior != result:
            return {"schemaVersion": CONTRACT_VERSION, "status": "DuplicateConflict", "runs": []}
        by_identity[identity] = result

    return {
        "schemaVersion": CONTRACT_VERSION,
        "status": "Ready",
        "runs": [by_identity[key] for key in sorted(by_identity)],
    }
