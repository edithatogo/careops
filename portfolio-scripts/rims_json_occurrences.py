"""Lossless-structure JSON occurrence projection for PRIVATE RIMS consumers.

This is NOT a public field profile: every original scalar value is included.
Never write the output to Git, logs, public dashboards or unrestricted Lists.
The original source bytes remain the authority for byte-level provenance.
"""
from __future__ import annotations

from hashlib import sha256
import json

MAX_BYTES = 12_000_000
MAX_DEPTH = 32
MAX_OCCURRENCES = 200_000

class OccurrenceError(ValueError):
    pass


def _no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise OccurrenceError("duplicate source JSON key")
        out[key] = value
    return out


def _constant(value):
    raise OccurrenceError("non-finite JSON numeric literal")


def _digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def _escape(key):
    return key.replace("~", "~0").replace("/", "~1")


def _unescape(key):
    if "~" in key:
        import re
        if re.search(r"~(?![01])", key):
            raise OccurrenceError("invalid JSON pointer escape")
    return key.replace("~1", "/").replace("~0", "~")


def _kind(value):
    if value is None: return "null"
    if isinstance(value, bool): return "boolean"
    if isinstance(value, int): return "integer"
    if isinstance(value, float): return "number"
    if isinstance(value, str): return "string"
    if isinstance(value, dict): return "object"
    if isinstance(value, list): return "array"
    raise OccurrenceError("invalid JSON value")


def expand(raw_bytes, *, source_id, record_id, source_sha256,
           verify_source=None):
    """Expand a pinned private JSON value; source verification is caller-owned."""
    if not isinstance(raw_bytes, bytes) or len(raw_bytes) > MAX_BYTES:
        raise OccurrenceError("bounded original JSON bytes required")
    actual = sha256(raw_bytes).hexdigest()
    if not isinstance(source_sha256, str) or actual != source_sha256:
        raise OccurrenceError("source byte SHA mismatch")
    if (not isinstance(source_id, str) or not source_id.strip() or
            not isinstance(record_id, str) or not record_id.strip()):
        raise OccurrenceError("source qualified identity required")
    if not callable(verify_source) or verify_source(source_id, record_id, actual) is not True:
        raise OccurrenceError("independent source authority required")
    try:
        original = json.loads(raw_bytes.decode("utf-8"),
                              object_pairs_hook=_no_duplicate_keys,
                              parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise OccurrenceError("invalid UTF-8 JSON source") from exc
    records = []
    def visit(value, path, semantic, depth):
        if depth > MAX_DEPTH or len(records) >= MAX_OCCURRENCES:
            raise OccurrenceError("source exceeds occurrence/depth limit")
        kind = _kind(value)
        records.append({"ordered_path": path, "semantic_path": semantic,
                        "kind": kind,
                        "value": value if kind not in ("object", "array") else None})
        if kind == "object":
            for key, item in value.items():
                visit(item, path + "/" + _escape(key),
                      semantic + "/" + _escape(key), depth + 1)
        elif kind == "array":
            for index, item in enumerate(value):
                visit(item, path + "/" + str(index),
                      semantic + "/[]", depth + 1)
    visit(original, "", "", 0)
    return {"schema": "careops-rims.private-json-occurrences/1",
            "source_id": source_id, "record_id": record_id,
            "source_sha256": actual,
            "canonical_semantic_sha256": _digest(original),
            "occurrence_count": len(records), "occurrences": records,
            "private_values": True, "native_admission_authorised": False,
            "byte_source_must_be_retained": True}


def reconstruct(projection):
    """Recreate the exact JSON value hierarchy (not source byte whitespace)."""
    if projection.get("schema") != "careops-rims.private-json-occurrences/1":
        raise OccurrenceError("wrong occurrence contract")
    rows = projection.get("occurrences")
    if not isinstance(rows, list) or not rows or len(rows) != projection.get("occurrence_count"):
        raise OccurrenceError("incomplete occurrence inventory")
    by_path = {}
    for item in rows:
        if not isinstance(item, dict):
            raise OccurrenceError("invalid occurrence")
        path = item.get("ordered_path")
        kind = item.get("kind")
        if not isinstance(path, str) or path in by_path or kind not in (
                "object", "array", "string", "integer", "number", "boolean", "null"):
            raise OccurrenceError("invalid duplicate path or kind")
        val = item.get("value")
        if kind in ("object", "array") and val is not None:
            raise OccurrenceError("container must not hold scalar value")
        if kind in ("string", "integer", "number", "boolean", "null") and _kind(val) != kind:
            raise OccurrenceError("type changed from source")
        by_path[path] = item
    if "" not in by_path:
        raise OccurrenceError("root occurrence absent")
    root_kind = by_path[""]["kind"]
    result = {} if root_kind == "object" else [] if root_kind == "array" else by_path[""]["value"]
    def order(path):
        tokens = path.split("/")[1:]
        parent = ""
        keys = []
        for token in tokens:
            if by_path.get(parent, {}).get("kind") == "array":
                if not token.isdigit() or str(int(token)) != token:
                    raise OccurrenceError("noncanonical array index")
                keys.append((0, int(token)))
            else:
                keys.append((1, token))
            parent += "/" + token
        return len(tokens), keys
    for path in sorted((p for p in by_path if p), key=order):
        tokens = path.split("/")[1:]
        parent = "" if len(tokens) == 1 else "/" + "/".join(tokens[:-1])
        if parent not in by_path:
            raise OccurrenceError("orphan occurrence")
        parent_kind = by_path[parent]["kind"]
        child_kind = by_path[path]["kind"]
        value = {} if child_kind == "object" else [] if child_kind == "array" else by_path[path]["value"]
        target = result
        for i, token in enumerate(tokens[:-1]):
            prefix = "" if i == 0 else "/" + "/".join(tokens[:i])
            kind = by_path[prefix]["kind"]
            token = _unescape(token)
            try:
                target = target[int(token)] if kind == "array" else target[token]
            except (IndexError, KeyError, ValueError, TypeError) as exc:
                raise OccurrenceError("unreachable nested occurrence") from exc
        name = _unescape(tokens[-1])
        if parent_kind == "object":
            if name in target:
                raise OccurrenceError("object field collision")
            target[name] = value
        elif parent_kind == "array":
            if not name.isdigit() or str(int(name)) != name or int(name) != len(target):
                raise OccurrenceError("non-sequential source array index")
            target.append(value)
        else:
            raise OccurrenceError("scalar parent cannot have children")
    if _digest(result) != projection.get("canonical_semantic_sha256"):
        raise OccurrenceError("reconstruction differs from source")
    return result
