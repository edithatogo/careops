"""Typed, evidence-bearing medallion records conforming to RIMS v1 JSON Schemas.

No external services, source collection, human decisions or report publication.
Historic medallion helpers remain available; this bridge builds v1 records
without silently converting source assertions to approvals.
"""
from __future__ import annotations

from hashlib import sha256
from datetime import datetime
import json
from pathlib import Path

LAYERS = ("bronze", "silver", "gold", "platinum")


class ContractViolation(ValueError):
    pass


def digest(value):
    try:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise ContractViolation("payload not JSON-serialisable") from exc
    return sha256(data).hexdigest()


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContractViolation("missing " + label)
    return value


def _utc(value):
    try:
        dt = datetime.fromisoformat(
            _text(value, "capture timestamp").replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ContractViolation("invalid capture timestamp") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ContractViolation("capture timestamp must have a timezone")


def load_schema(layer, *, directory=None):
    if layer not in LAYERS:
        raise ContractViolation("unknown medallion layer")
    root = Path(directory) if directory is not None else (
        Path(__file__).resolve().parents[1] /
        "portfolio/rims/contracts/medallion"
    )
    return json.loads((root / (layer + ".schema.json")).read_text(encoding="utf-8"))


def check_record_shape(layer, record, *, directory=None):
    """Check contractual keys, not a substitute for full JSON Schema validation.

    Use jsonschema Draft202012Validator in a qualified CI environment.
    """
    schema = load_schema(layer, directory=directory)
    if not isinstance(record, dict):
        raise ContractViolation("medallion record must be object")
    missing = set(schema["required"]) - set(record)
    extra = set(record) - set(schema["properties"])
    if missing or extra:
        raise ContractViolation(
            "contract fields missing or extra: " +
            str((sorted(missing), sorted(extra)))
        )
    _text(record["source_id"], "source_id")
    _text(record["record_id"], "record_id")
    return True


def bronze_record(source_id, record_id, raw_payload, *, provider, licence,
                  capture_timestamp, retention_class, pagination,
                  source_schema_uri=None, source_record_id=None,
                  ingestion_status="complete", original_capture_sha256=None):
    """Hash canonical rights-approved JSON unless caller supplied verified bytes.

    A caller-supplied upstream digest is an *assertion*, not independently
    verified raw-byte provenance. Preserve original bytes in a private archive.
    """
    for value, label in (
        (source_id, "source_id"), (record_id, "record_id"),
        (provider, "provider"), (licence, "licence"),
        (retention_class, "retention_class"),
    ):
        _text(value, label)
    _utc(capture_timestamp)
    if not isinstance(raw_payload, (dict, list)):
        raise ContractViolation("source payload must be object or array")
    if ingestion_status not in ("complete", "partial", "failed", "denied"):
        raise ContractViolation("invalid ingestion status")
    if not isinstance(pagination, dict) or (
        pagination.get("complete") is not True and ingestion_status == "complete"
    ):
        raise ContractViolation("complete source requires complete pagination")
    if original_capture_sha256 is not None:
        if (
            not isinstance(original_capture_sha256, str) or
            len(original_capture_sha256) != 64 or
            any(c not in "0123456789abcdef" for c in original_capture_sha256)
        ):
            raise ContractViolation("invalid upstream digest")
    return {
        "schema_version": "1", "source_id": source_id, "record_id": record_id,
        "raw_payload": raw_payload, "source_record_id": source_record_id or record_id,
        "source_schema_uri": source_schema_uri, "provider": provider,
        "licence": licence, "capture_timestamp": capture_timestamp,
        "pagination": pagination,
        "capture_sha256": original_capture_sha256 or digest(raw_payload),
        "retention_class": retention_class, "ingestion_status": ingestion_status,
    }


def silver_record(bronze, *, canonical_id, entity_type, mapping,
                  relationships=(), ambiguities=()):
    if (
        bronze.get("ingestion_status") != "complete" or
        bronze.get("pagination", {}).get("complete") is not True
    ):
        raise ContractViolation("incomplete Bronze capture cannot be normalised")
    raw = bronze["raw_payload"]
    if not isinstance(raw, dict):
        raise ContractViolation(
            "array root requires explicit source-record partition"
        )
    _text(canonical_id, "canonical_id")
    _text(entity_type, "entity_type")
    if not isinstance(mapping, dict) or not set(mapping).issubset(raw):
        raise ContractViolation("unresolved source field mapping")
    if "_retained_unmapped" in mapping.values():
        raise ContractViolation("reserved Silver field")
    if len(set(mapping.values())) != len(mapping):
        raise ContractViolation("colliding canonical field names")
    if not all(isinstance(v, str) and v.strip() for v in mapping.values()):
        raise ContractViolation("invalid canonical field")
    attributes = {target: raw[source] for source, target in mapping.items()}
    unmapped = {field: value for field, value in raw.items() if field not in mapping}
    if unmapped:
        attributes["_retained_unmapped"] = unmapped
    lineage = [
        {"source_field": source, "target_field": target,
         "disposition": "mapped"}
        for source, target in sorted(mapping.items())
    ] + [
        {"source_field": source,
         "target_field": "_retained_unmapped." + source,
         "disposition": "retained_only"}
        for source in sorted(unmapped)
    ]
    return {
        "schema_version": "1",
        "source_id": bronze["source_id"], "record_id": bronze["record_id"],
        "canonical_id": canonical_id, "entity_type": entity_type,
        "typed_attributes": attributes, "relationships": list(relationships),
        "original_capture_sha256": bronze["capture_sha256"],
        "field_lineage": lineage, "ambiguities": list(ambiguities),
        "source_snapshot": bronze["capture_sha256"],
    }


def gold_record(records, *, product_source_id, view_id, period, alias_version,
                verify_decision=None, decision_by_id=None):
    """Approved output is identifier-only, never private raw attributes."""
    if not isinstance(records, list) or not isinstance(decision_by_id, dict):
        raise ContractViolation("records and current decisions required")
    for value, label in (
        (product_source_id, "product_source_id"),
        (view_id, "view_id"), (alias_version, "alias_version"),
    ):
        _text(value, label)
    seen, approved, held, source_revisions = set(), [], [], set()
    for row in records:
        key = _text(row.get("canonical_id"), "canonical ID")
        if key in seen:
            raise ContractViolation("duplicate canonical ID")
        seen.add(key)
        source_revisions.add(
            _text(row.get("original_capture_sha256"), "source revision")
        )
        decision = decision_by_id.get(key)
        if (
            decision and
            decision.get("assertion_type") == "publication" and
            decision.get("status") == "ConfirmedCHHHS" and
            callable(verify_decision) and
            verify_decision(decision, row) is True
        ):
            approved.append({
                "canonical_id": key,
                "verified_decision_id": _text(
                    decision.get("decision_id"), "decision ID"
                ),
            })
        else:
            held.append(key)
    counts = {
        "source": len(seen), "approved": len(approved), "held": len(held)
    }
    status = (
        "verified" if approved and not held
        else "mixed" if approved else "pending"
    )
    snapshot = digest({
        "period": period, "view_id": view_id, "approved": approved,
        "held": sorted(held),
        "source_revisions": sorted(source_revisions),
    })
    return {
        "schema_version": "1", "source_id": product_source_id,
        "record_id": view_id + ":" + (period or "all") + ":" + snapshot[:16],
        "view_id": view_id, "grain": "canonical-publication",
        "period": period, "rows": approved,
        "source_revisions": sorted(source_revisions),
        "population_counts": counts, "review_status": status,
        "field_alias_version": alias_version, "snapshot_sha256": snapshot,
    }


def platinum_record(gold, *, intelligence_id, hypothesis, claims,
                    methods, uncertainty, evidence_refs, limitations,
                    decision_owner):
    for value, label in (
        (intelligence_id, "intelligence_id"),
        (hypothesis, "hypothesis"), (decision_owner, "decision_owner"),
    ):
        _text(value, label)
    if not isinstance(claims, list) or not isinstance(methods, dict) or not isinstance(uncertainty, dict):
        raise ContractViolation("claims, methods and uncertainty must be explicit")
    if any(not isinstance(claim, dict) or not claim.get("evidence_refs") for claim in claims):
        raise ContractViolation("every claim requires explicit supporting evidence")
    if not isinstance(evidence_refs, list) or not evidence_refs or not all(
        isinstance(item, str) and item for item in evidence_refs
    ):
        raise ContractViolation("evidence references required")
    if not isinstance(limitations, list):
        raise ContractViolation("limitations required")
    return {
        "schema_version": "1", "source_id": gold["source_id"],
        "record_id": intelligence_id, "intelligence_id": intelligence_id,
        "hypothesis": hypothesis, "claims": claims,
        "methods": methods, "uncertainty": uncertainty,
        "evidence_refs": evidence_refs, "limitations": limitations,
        "human_release_required": True, "decision_owner": decision_owner,
        "input_gold_revision": gold["snapshot_sha256"],
    }
