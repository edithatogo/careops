"""Auditable source-level RIMS contract completeness report.

A schema's existence is not proof that it is precise, implemented for all
domains, connected to retained data or admitted in the live tenant.
"""
from __future__ import annotations

import json
from pathlib import Path


MEDALLION = ("bronze", "silver", "gold", "platinum")
DOMAINS = ("publications", "people", "organisations",
           "projects_studies", "funding", "shared")
PERMISSIVE = {"object", "array", "string", "number", "boolean", "null"}


def audit(root=None):
    repo = Path(root) if root else Path(__file__).resolve().parents[1]
    base = repo / "portfolio/rims/contracts"
    medallion, domains = {}, {}
    for name in MEDALLION:
        schema = json.loads(
            (base / "medallion" / (name + ".schema.json")).read_text()
        )
        props = set(schema["properties"])
        required = set(schema["required"])
        medallion[name] = {
            "schema_exists": True,
            "declared_properties": len(props),
            "required_properties": len(required),
            "required_are_declared": required.issubset(props),
            "strict_root": schema.get("additionalProperties") is False,
            "bridge_available": True,
            "native_conformance": "unverified",
        }
    for name in DOMAINS:
        schema = json.loads(
            (base / "domains" / (name + ".schema.json")).read_text()
        )
        broad = []
        for field, rule in schema["properties"].items():
            types = rule.get("type")
            if isinstance(types, list) and set(types) == PERMISSIVE:
                broad.append(field)
        domains[name] = {
            "schema_exists": True,
            "declared_properties": len(schema["properties"]),
            "unconstrained_optional_fields": len(broad),
            "broad_field_names": sorted(broad),
            "unknown_fields_allowed": schema.get("additionalProperties", True),
            "full_typed_runtime": False,
            "retained_data_coverage": "not_measured",
            "native_model_report_parity": "not_verified",
        }
    return {
        "schema": "careops-rims.contract-coverage-audit/1",
        "medallion": medallion, "domains": domains,
        "source_level_bridge_status": "publications_only_synthetic",
        "cross_domain_analytics": "synthetic_descriptive_only",
        "tenant_acceptance": False,
        "all_contracts_fully_implemented": False,
        "all_source_fields_fully_used": False,
    }


def main():
    print(json.dumps(audit(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
