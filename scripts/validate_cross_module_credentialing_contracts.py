from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "portfolio" / "credentialing-mvp-compatibility.json"
MATRIX_PATH = ROOT / "portfolio" / "credentialing-contract-matrix.json"
DOCUMENTATION_KEYS = {"$id", "title", "description", "$comment", "examples"}
FORBIDDEN_FIXTURE_KEYS = {
    "name",
    "email",
    "emailAddress",
    "registrationNumber",
    "qualification",
    "scopeText",
    "decisionReason",
    "patientData",
    "rawPayload",
}

MODULE_DIRECTORIES = {
    "careops-approve": "careops-approve",
    "careops-decisions": "careops-decisions",
    "careops-process": "careops-process",
    "careops-legacy-migration": "careops-legacy-migration",
}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        message = f"Expected JSON object: {path}"
        raise TypeError(message)
    return cast("dict[str, object]", value)


def canonical_contract(value: object) -> object:
    if isinstance(value, dict):
        mapping = cast("dict[str, object]", value)
        return {
            key: canonical_contract(child)
            for key, child in sorted(mapping.items())
            if key not in DOCUMENTATION_KEYS
        }
    if isinstance(value, list):
        return [canonical_contract(child) for child in cast("list[object]", value)]
    return value


def git_head(path: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def normalise_key(value: object) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())


def find_forbidden_key(value: object, path: str = "$") -> str | None:
    if isinstance(value, dict):
        mapping = cast("dict[object, object]", value)
        for key, child in mapping.items():
            if normalise_key(key) in {
                normalise_key(candidate) for candidate in FORBIDDEN_FIXTURE_KEYS
            }:
                return f"{path}.{key}"
            nested = find_forbidden_key(child, f"{path}.{key}")
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(cast("list[object]", value)):
            nested = find_forbidden_key(child, f"{path}[{index}]")
            if nested is not None:
                return nested
    return None


def schema_required(schema: dict[str, object]) -> set[str]:
    return set(cast("list[str]", schema.get("required", [])))


def schema_properties(schema: dict[str, object]) -> dict[str, dict[str, object]]:
    return cast("dict[str, dict[str, object]]", schema.get("properties", {}))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def validate_exact_schema_pair(
    left: dict[str, object],
    right: dict[str, object],
    label: str,
    failures: list[str],
) -> None:
    require(
        canonical_contract(left) == canonical_contract(right),
        f"{label} schemas differ after documentation-only fields are removed",
        failures,
    )


def validate_source_record_compatibility(
    provider: dict[str, object],
    consumer: dict[str, object],
    failures: list[str],
) -> None:
    provider_required = schema_required(provider)
    consumer_required = schema_required(consumer)
    require(
        provider_required == consumer_required,
        "Legacy source provider and Approve consumer require different fields",
        failures,
    )
    require(
        provider.get("additionalProperties") is False
        and consumer.get("additionalProperties") is False,
        "Source-record schemas must fail closed on unexpected top-level fields",
        failures,
    )
    provider_properties = schema_properties(provider)
    consumer_properties = schema_properties(consumer)
    for property_name in provider_required:
        require(
            property_name in consumer_properties,
            f"Approve source-record consumer is missing {property_name}",
            failures,
        )
    for property_name in (
        "contractVersion",
        "sourceMode",
        "rawPayloadStored",
        "reconciliationStatus",
    ):
        require(
            canonical_contract(provider_properties[property_name])
            == canonical_contract(consumer_properties[property_name]),
            f"Source-record constraint differs for {property_name}",
            failures,
        )


def validate_fixture_against_schema(
    fixture: dict[str, object],
    schema: dict[str, object],
    label: str,
    failures: list[str],
) -> None:
    required = schema_required(schema)
    properties = schema_properties(schema)
    fixture_keys = set(fixture)
    require(required <= fixture_keys, f"{label} fixture lacks required fields", failures)
    if schema.get("additionalProperties") is False:
        require(
            fixture_keys <= set(properties),
            f"{label} fixture contains fields outside the schema",
            failures,
        )
    for key, property_schema in properties.items():
        if key not in fixture:
            continue
        if "const" in property_schema:
            require(
                fixture[key] == property_schema["const"],
                f"{label} fixture violates const for {key}",
                failures,
            )
        if "enum" in property_schema:
            require(
                fixture[key] in cast("list[object]", property_schema["enum"]),
                f"{label} fixture violates enum for {key}",
                failures,
            )
    forbidden = find_forbidden_key(fixture)
    require(forbidden is None, f"{label} fixture contains prohibited key {forbidden}", failures)


def validate_process_contract(
    schema: dict[str, object],
    failures: list[str],
) -> None:
    properties = schema_properties(schema)
    require(
        cast("dict[str, object]", properties.get("contract_version", {})).get("const")
        == "0.1.0",
        "Process event contract version must be 0.1.0",
        failures,
    )
    require(
        cast("dict[str, object]", properties.get("ontology_version", {})).get("const")
        == "0.1.0",
        "Process event ontology version must be 0.1.0",
        failures,
    )
    source_values = set(
        cast(
            "list[str]",
            cast("dict[str, object]", properties.get("source", {})).get("enum", []),
        )
    )
    require(
        {"careops-approve", "careops-decisions"} <= source_values,
        "Process event contract must accept Approve and Decisions sources",
        failures,
    )
    definitions = cast("dict[str, dict[str, object]]", schema.get("$defs", {}))
    fact = definitions.get("fact", {})
    fact_properties = schema_properties(fact)
    require(
        fact.get("additionalProperties") is False,
        "Process event facts must reject unexpected fields",
        failures,
    )
    require(
        {
            "event_id",
            "activity",
            "timestamp_utc",
            "source_system",
            "object_ids",
            "observed_or_inferred",
            "confidence",
            "qualifiers",
        }
        <= schema_required(fact),
        "Process event fact contract is incomplete",
        failures,
    )
    qualifiers = cast(
        "dict[str, object]",
        fact_properties.get("qualifiers", {}),
    )
    require(
        qualifiers.get("additionalProperties") is False,
        "Process event qualifiers must be allowlisted",
        failures,
    )
    require(
        bool(cast("list[object]", fact.get("allOf", []))),
        "Process event contract must distinguish observed confidence",
        failures,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_json(MANIFEST_PATH)
    matrix = load_json(MATRIX_PATH)
    modules = cast("dict[str, dict[str, object]]", manifest["modules"])
    failures: list[str] = []

    roots = {
        name: args.module_root / directory
        for name, directory in MODULE_DIRECTORIES.items()
    }
    for name, root in roots.items():
        require(root.is_dir(), f"Missing checked-out module {name}", failures)
        if root.is_dir():
            require(
                git_head(root) == modules[name]["commit"],
                f"Checked-out {name} commit differs from the release manifest",
                failures,
            )

    approve_packet = load_json(
        roots["careops-approve"]
        / "contracts"
        / "credentialing-governance-packet.schema.json"
    )
    decisions_packet = load_json(
        roots["careops-decisions"]
        / "powerplatform"
        / "src"
        / "contracts"
        / "credentialing-governance-packet.schema.json"
    )
    approve_result = load_json(
        roots["careops-approve"] / "contracts" / "credentialing-result.schema.json"
    )
    decisions_result = load_json(
        roots["careops-decisions"]
        / "powerplatform"
        / "src"
        / "contracts"
        / "credentialing-result.schema.json"
    )
    legacy_source = load_json(
        roots["careops-legacy-migration"]
        / "contracts"
        / "existing-system-source-record.schema.json"
    )
    approve_source = load_json(
        roots["careops-approve"]
        / "contracts"
        / "existing-system-source-record.schema.json"
    )
    process_events = load_json(
        roots["careops-process"]
        / "contracts"
        / "credentialing-event-projection.json"
    )

    validate_exact_schema_pair(
        approve_packet,
        decisions_packet,
        "governance packet",
        failures,
    )
    validate_exact_schema_pair(
        approve_result,
        decisions_result,
        "decision result",
        failures,
    )
    validate_source_record_compatibility(legacy_source, approve_source, failures)
    validate_process_contract(process_events, failures)

    approve_packet_fixture = load_json(
        roots["careops-approve"]
        / "contracts"
        / "fixtures"
        / "credentialing-governance-packet.valid.json"
    )
    approve_result_fixture = load_json(
        roots["careops-approve"]
        / "contracts"
        / "fixtures"
        / "credentialing-result.valid.json"
    )
    validate_fixture_against_schema(
        approve_packet_fixture,
        decisions_packet,
        "governance packet",
        failures,
    )
    validate_fixture_against_schema(
        approve_result_fixture,
        decisions_result,
        "decision result",
        failures,
    )

    interfaces = cast("list[dict[str, object]]", matrix["interfaces"])
    require(
        all(interface.get("productionWrite") is False for interface in interfaces),
        "Cross-module matrix contains a production-write interface",
        failures,
    )

    receipt = {
        "schemaVersion": 1,
        "releaseTrain": manifest["releaseTrain"],
        "moduleCommits": {
            name: modules[name]["commit"] for name in MODULE_DIRECTORIES
        },
        "checks": {
            "immutableCheckouts": not any(
                "Checked-out" in failure for failure in failures
            ),
            "governancePacketCompatible": not any(
                "governance packet" in failure.lower() for failure in failures
            ),
            "decisionResultCompatible": not any(
                "decision result" in failure.lower() for failure in failures
            ),
            "sourceRecordCompatible": not any(
                "Source-record" in failure for failure in failures
            ),
            "processEventBoundaryValid": not any(
                "Process event" in failure for failure in failures
            ),
            "noProductionWrites": not any(
                "production-write" in failure for failure in failures
            ),
        },
        "passed": not failures,
        "evidenceCeiling": (
            "Cross-repository source-contract compatibility and synthetic fixture "
            "behaviour only; not tenant deployment or operating effectiveness."
        ),
    }
    if args.receipt is not None:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
