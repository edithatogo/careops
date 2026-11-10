"""Optional offline SQLite materialisation from an authorised RIMS JSON snapshot.

Standard library only. SQLite is not a Power Automate cloud flow connector;
derive it from committed, independently verified source data in an approved
local runtime. Exact decimals/dates remain typed TEXT with schema metadata.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sqlite3

_source = Path(__file__).with_name("rims_file_snapshot.py")
_spec = importlib.util.spec_from_file_location("rims_file_snapshot", _source)
_snapshot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_snapshot)
_COLUMN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
_SQL_TYPES = {"string": "TEXT", "integer": "INTEGER", "number": "REAL",
              "boolean": "INTEGER", "object": "TEXT", "array": "TEXT"}


class CacheRefused(ValueError):
    pass


def materialize(bundle, path, *, verify_committed=None):
    """Build an immutable-cache candidate after independent commit verification."""
    if not callable(verify_committed) or verify_committed(bundle["manifest"]) is not True:
        raise CacheRefused("authoritative native committed snapshot not verified")
    data, schema, manifest = bundle["rows"], bundle["json_schema"], bundle["manifest"]
    _snapshot.verify_readback(bundle, persisted_rows=data, persisted_schema=schema)
    properties = schema.get("items", {}).get("properties", {})
    if not isinstance(properties, dict) or not properties:
        raise CacheRefused("invalid typed schema")
    fields = list(properties)
    if any(not _COLUMN.fullmatch(name) for name in fields):
        raise CacheRefused("unsafe column name")
    definitions = []
    for field in fields:
        value = properties[field]["type"]
        allowed = value if isinstance(value, list) else [value]
        kind = next((name for name in allowed if name != "null"), None)
        if kind not in _SQL_TYPES:
            raise CacheRefused("unknown field datatype")
        definitions.append(f'"{field}" {_SQL_TYPES[kind]}')
    target = Path(path)
    if target.exists():
        raise CacheRefused("refuse overwrite of existing cache")
    if sqlite3.sqlite_version_info < (3, 37, 0):
        raise CacheRefused("SQLite STRICT support required")
    try:
        with sqlite3.connect(target) as conn:
            conn.execute("CREATE TABLE records (" + ", ".join(definitions) + ") STRICT")
            conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL) STRICT")
            for row in data["rows"]:
                values = []
                for name in fields:
                    item = row.get(name)
                    kind = properties[name]["type"]
                    kind = next((v for v in kind if v != "null"), None) if isinstance(kind, list) else kind
                    if kind in ("object", "array") and item is not None:
                        item = json.dumps(item, ensure_ascii=False, sort_keys=True)
                    elif kind == "boolean" and item is not None:
                        item = int(item)
                    values.append(item)
                conn.execute("INSERT INTO records VALUES (" + ",".join("?" for _ in fields) + ")", values)
            for name, value in (("source_id", manifest["source_id"]),
                                ("run_id", manifest["run_id"]),
                                ("rows_sha256", manifest["rows_sha256"]),
                                ("json_schema", json.dumps(schema, sort_keys=True))):
                conn.execute("INSERT INTO metadata VALUES (?, ?)", (name, value))
            count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            if count != manifest["count"]:
                raise CacheRefused("row count mismatch")
        return {"path": str(target), "row_count": count, "schema_preserved": True,
                "native_authority": False}
    except Exception:
        target.unlink(missing_ok=True)
        raise
