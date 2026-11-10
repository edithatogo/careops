"""Bounded field-level utilisation profiling of already retained RIMS source data.

Pure and tenant-free. Profile nested leaf paths, exact missing/null/empty status,
type variation and consumer utilisation without publishing raw source values.
Do not infer that a populated source field is used by a report, or that a
provider's full schema is present in a captured subset.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from typing import Any

CONSUMERS = frozenset({"silver", "gold", "semantic_model", "dashboard",
                       "scorecard", "paginated_report", "decision",
                       "platinum", "offline_export"})
DISPOSITIONS = frozenset({"mapped", "retained_only", "excluded"})
MAX_RECORDS = 100_000
MAX_PATHS = 10_000
MAX_DEPTH = 24


class UtilisationError(ValueError):
    pass


def _digest(value: Any) -> str:
    try:
        serialised = json.dumps(value, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise UtilisationError("non-JSON source value") from exc
    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()


def _value_kind(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    raise UtilisationError("unsupported source value")


def _escape(key: str) -> str:
    return key.replace("~", "~0").replace("/", "~1")


def _paths(value: Any, prefix: str, depth: int):
    if depth > MAX_DEPTH:
        raise UtilisationError("source exceeds maximum nesting")
    if isinstance(value, dict):
        if not value:
            yield prefix or "/", value
        else:
            for name, child in value.items():
                if not isinstance(name, str):
                    raise UtilisationError("source object key must be text")
                yield from _paths(child, prefix + "/" + _escape(name), depth + 1)
    elif isinstance(value, list):
        # Repeated array elements contribute one *field path*, not index-specific
        # schema columns. Empty arrays remain visible as a typed observation.
        if not value:
            yield prefix or "/", value
        else:
            for item in value:
                yield from _paths(item, prefix + "/[]", depth + 1)
    else:
        yield prefix or "/", value


def profile(source_id: str, records: list[dict], *, source_sha256: str,
            declared_paths: list[str] | None = None) -> dict:
    """Summarise source payloads; no raw values or record identities returned.

    The source digest is asserted by caller and must be verified independently
    against the retained private archive before using this as evidence.
    """
    if not isinstance(source_id, str) or not source_id.strip():
        raise UtilisationError("source ID required")
    if not isinstance(source_sha256, str) or len(source_sha256) != 64 or any(
        ch not in "0123456789abcdef" for ch in source_sha256
    ):
        raise UtilisationError("source SHA-256 required")
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise UtilisationError("record array unavailable or unbounded")
    if not all(isinstance(row, dict) for row in records):
        raise UtilisationError("records must be source objects")
    if declared_paths is not None and (
        not isinstance(declared_paths, list) or
        len(declared_paths) > MAX_PATHS or
        any(not isinstance(p, str) or not p.startswith("/") for p in declared_paths) or
        len(set(declared_paths)) != len(declared_paths)
    ):
        raise UtilisationError("declared field paths invalid")
    path_counts = defaultdict(Counter)
    present_per_record = Counter()
    for row in records:
        observed = set()
        # This validates primitive values and rejects non-JSON forms via digest.
        _digest(row)
        for path, value in _paths(row, "", 0):
            if len(path_counts) >= MAX_PATHS and path not in path_counts:
                raise UtilisationError("too many distinct source paths")
            kind = _value_kind(value)
            path_counts[path]["occurrences"] += 1
            path_counts[path]["type:" + kind] += 1
            if kind == "null":
                path_counts[path]["null_occurrences"] += 1
            if value == "" or value == [] or value == {}:
                path_counts[path]["empty_occurrences"] += 1
            if kind not in ("null",) and value not in ("", [], {}):
                path_counts[path]["nonempty_occurrences"] += 1
            observed.add(path)
        for path in observed:
            present_per_record[path] += 1
    all_paths = set(path_counts) | set(declared_paths or [])
    fields = []
    for path in sorted(all_paths):
        value = path_counts.get(path, Counter())
        fields.append({
            "path": path,
            "records_present": present_per_record[path],
            "records_missing": len(records) - present_per_record[path],
            "occurrences": value["occurrences"],
            "null_occurrences": value["null_occurrences"],
            "empty_occurrences": value["empty_occurrences"],
            "nonempty_occurrences": value["nonempty_occurrences"],
            "types": sorted(k[5:] for k in value if k.startswith("type:")),
            "declared_by_provider": None if declared_paths is None else path in declared_paths,
        })
    return {
        "schema": "careops-rims.retained-field-profile/1",
        "source_id": source_id, "asserted_source_sha256": source_sha256,
        "source_digest_independently_verified": False,
        "records_observed": len(records),
        "paths_observed": len(path_counts),
        "paths_declared": None if declared_paths is None else len(declared_paths),
        "fields": fields, "contains_values": False,
        "full_provider_schema_coverage_verified": False,
        "native_consumer_coverage_verified": False,
    }


def utilisation(profile_result: dict, mappings: list[dict]) -> dict:
    """Separate actual consumer linkage from mere source capture and retention.

    For a consumer to count as used, supply a source-derived path/consumer
    mapping with an exact consumer artifact identity and revision. A mapping
    string alone is *declared* utilisation and requires native readback.
    """
    if profile_result.get("schema") != "careops-rims.retained-field-profile/1":
        raise UtilisationError("invalid field profile")
    if not isinstance(mappings, list):
        raise UtilisationError("mappings must be an array")
    observed = {row["path"] for row in profile_result["fields"]}
    by_path = defaultdict(list)
    seen = set()
    for item in mappings:
        if not isinstance(item, dict):
            raise UtilisationError("mapping object required")
        path, target = item.get("source_path"), item.get("consumer")
        disposition = item.get("disposition")
        if path not in observed or disposition not in DISPOSITIONS:
            raise UtilisationError("source path or disposition invalid")
        if disposition == "mapped":
            if target not in CONSUMERS or not all(
                isinstance(item.get(k), str) and item[k].strip()
                for k in ("artifact_id", "artifact_revision", "target_field")
            ):
                raise UtilisationError("concrete consumer artifact and field required")
        elif target is not None:
            raise UtilisationError("retained/excluded fields have no consuming artifact")
        if disposition == "excluded" and not (
            isinstance(item.get("reason"), str) and item["reason"].strip()
        ):
            raise UtilisationError("excluded field needs rights/security reason")
        if disposition == "retained_only" and not (
            isinstance(item.get("reason"), str) and item["reason"].strip()
        ):
            raise UtilisationError("retained field needs reason or pending consumer")
        key = (path, disposition, target, item.get("artifact_id"))
        if key in seen:
            raise UtilisationError("duplicate utilisation link")
        seen.add(key)
        by_path[path].append(item)
    used, retained, excluded, unassessed = [], [], [], []
    for path in sorted(observed):
        entries = by_path.get(path, [])
        classes = {entry["disposition"] for entry in entries}
        if "mapped" in classes and len(classes) > 1:
            raise UtilisationError("path cannot be mapped and retained/excluded")
        if classes == {"retained_only", "excluded"}:
            raise UtilisationError("path cannot be retained and excluded")
        if "mapped" in classes:
            used.append(path)
        elif "excluded" in classes:
            excluded.append(path)
        elif "retained_only" in classes:
            retained.append(path)
        else:
            unassessed.append(path)
    return {
        "schema": "careops-rims.retained-field-utilisation/1",
        "source_id": profile_result["source_id"],
        "source_field_count": len(observed),
        "mapped_to_consumer": len(used),
        "retained_only": len(retained),
        "excluded_with_reason": len(excluded),
        "unassessed": len(unassessed),
        "unassessed_paths": unassessed,
        "paths_by_consumer": {
            name: sum(
                any(entry.get("consumer") == name
                    for entry in by_path.get(path, [])) for path in observed
            )
            for name in sorted(CONSUMERS)
        },
        "all_paths_accounted_for": not unassessed,
        "all_paths_used": not retained and not excluded and not unassessed,
        "consumer_binding_native_verified": False,
        "full_provider_schema_coverage_verified": False,
    }
