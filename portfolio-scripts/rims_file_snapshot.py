"""Tenant-free typed snapshot preparation for standard SharePoint file writes.

No Power Platform connection, manifest publication, recipient send or file write.
Native solution-aware flow must stage, read back and commit separately.
"""
from __future__ import annotations
import hashlib
import json

TYPES = {"string", "integer", "number", "boolean", "object", "array"}


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def build(source_id, run_id, rows, fields, *, captured_utc, source_revision, complete):
    if not complete:
        raise ValueError("incomplete source cannot become a committed snapshot")
    if not all(isinstance(x, str) and x for x in (source_id, run_id, captured_utc, source_revision)):
        raise ValueError("missing identity or capture time")
    if not isinstance(rows, list) or not all(isinstance(x, dict) for x in rows):
        raise ValueError("rows must be objects")
    if not isinstance(fields, list) or not fields:
        raise ValueError("field contract required")
    properties = {}
    for field in fields:
        if not isinstance(field, dict) or not isinstance(field.get("name"), str):
            raise ValueError("invalid field definition")
        name, kind = field["name"], field.get("type")
        if not name or name in properties or kind not in TYPES:
            raise ValueError("duplicate or invalid typed field")
        spec = {"type": [kind, "null"] if field.get("nullable") else kind}
        if field.get("format"):
            spec["format"] = field["format"]
        properties[name] = spec
    required = {field["name"] for field in fields if not field.get("nullable")}
    for row in rows:
        if not required.issubset(row):
            raise ValueError("required source field absent")
        if not set(row).issubset(properties):
            raise ValueError("unmapped source field: preserve source in Bronze instead")
        for name, value in row.items():
            spec = properties[name]
            choices = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
            if value is None:
                if "null" not in choices:
                    raise ValueError("unexpected null")
                continue
            test = {"string": lambda: isinstance(value, str),
                    "integer": lambda: type(value) is int,
                    "number": lambda: type(value) in (int, float),
                    "boolean": lambda: type(value) is bool,
                    "object": lambda: isinstance(value, dict),
                    "array": lambda: isinstance(value, list)}
            if not any(test[c]() for c in choices if c != "null"):
                raise ValueError("field datatype mismatch")
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema",
              "type": "array", "items": {"type": "object", "properties": properties,
              "additionalProperties": False},
              "x-note": "Timestamps and exact-decimal numbers must use typed string conventions."}
    data = {"schema": "careops-rims.snapshot/1", "source_id": source_id,
            "run_id": run_id, "captured_utc": captured_utc,
            "source_revision": source_revision, "rows": rows}
    manifest = {"schema": "careops-rims.snapshot-manifest/1",
                "source_id": source_id, "run_id": run_id,
                "status": "staged", "count": len(rows),
                "rows_sha256": _hash(data), "schema_sha256": _hash(schema),
                "native_committed": False}
    return {"rows": data, "json_schema": schema, "manifest": manifest}


def verify_readback(snapshot, *, persisted_rows, persisted_schema):
    marker = snapshot["manifest"]
    if _hash(persisted_rows) != marker["rows_sha256"]:
        raise ValueError("persisted rows not equal to staging source")
    if _hash(persisted_schema) != marker["schema_sha256"]:
        raise ValueError("persisted schema not equal to staging source")
    if len(persisted_rows.get("rows", [])) != marker["count"]:
        raise ValueError("row count changed")
    if persisted_rows.get("source_id") != marker["source_id"] or persisted_rows.get("run_id") != marker["run_id"]:
        raise ValueError("source identity mismatch")
    return {"readback_valid": True, "native_commit_authorised": False,
            "next_action": "qualified native completion-marker step only"}
