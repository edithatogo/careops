# SPDX-License-Identifier: Apache-2.0
"""Plan and verify a lossless, offline assessment-history compaction.

The returned archive is the exact UTF-8 preimage, not a rewritten serialization.
No file, network, or native operation is performed by this module.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from urllib.parse import urlsplit

HISTORY_FIELDS = ("assessmentReviewAddenda", "relationshipInventoryReconciliations")
ARCHIVE_FIELD = "assessmentHistoryArchives"
SCHEMA = "ppg-assessment-history-archive-v1"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse(text: str) -> dict:
    def reject_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")

    try:
        result = json.loads(text, object_pairs_hook=_object_pairs, parse_constant=reject_constant)
    except (TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("manifest must be a valid JSON object") from exc
    if not isinstance(result, dict):
        raise ValueError("manifest must be a JSON object")
    for field in HISTORY_FIELDS:
        if field in result and not isinstance(result[field], list):
            raise ValueError(f"{field} must be an array")
    if ARCHIVE_FIELD in result and not isinstance(result[ARCHIVE_FIELD], list):
        raise ValueError(f"{ARCHIVE_FIELD} must be an array")
    return result


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _top_spans(text: str) -> dict:
    """Locate top-level raw value tokens without reserializing their contents."""
    decoder = json.JSONDecoder()
    whitespace = " \t\r\n"
    i = 0
    while text[i] in whitespace:
        i += 1
    i += 1  # opening object brace, already validated by _parse
    spans = {}
    while True:
        while text[i] in whitespace:
            i += 1
        if text[i] == "}":
            return spans
        key, end = decoder.raw_decode(text, i)
        i = end
        while text[i] in whitespace:
            i += 1
        if text[i] != ":":
            raise ValueError("invalid object separator")
        i += 1
        while text[i] in whitespace:
            i += 1
        start = i
        _, i = decoder.raw_decode(text, i)
        spans[key] = (start, i)
        while text[i] in whitespace:
            i += 1
        if text[i] == ",":
            i += 1
        elif text[i] != "}":
            raise ValueError("invalid object separator")


def _last_array_token(raw: str) -> str:
    decoder = json.JSONDecoder()
    whitespace = " \t\r\n"
    i = 1
    last = None
    while True:
        while raw[i] in whitespace:
            i += 1
        if raw[i] == "]":
            return "[]" if last is None else "[" + last + "]"
        start = i
        _, i = decoder.raw_decode(raw, i)
        last = raw[start:i]
        while raw[i] in whitespace:
            i += 1
        if raw[i] == ",":
            i += 1
        elif raw[i] != "]":
            raise ValueError("invalid array separator")


def _summaries(text: str, original: dict) -> dict:
    spans = _top_spans(text)
    result = {}
    for field in HISTORY_FIELDS:
        present = field in original
        raw = text[slice(*spans[field])] if present else "[]"
        result[field] = {"present": present, "count": len(original.get(field, [])),
                         "sha256": _sha(raw.encode("utf-8"))}
    return result


def _compact(text: str, original: dict, ref: dict) -> str:
    spans = _top_spans(text)
    edits = []
    for field in HISTORY_FIELDS:
        if field in spans:
            start, end = spans[field]
            edits.append((start, end, _last_array_token(text[start:end])))
    encoded_ref = _json(ref)
    if ARCHIVE_FIELD in spans:
        start, end = spans[ARCHIVE_FIELD]
        raw = text[start:end]
        closing = raw.rfind("]")
        separator = "," if original[ARCHIVE_FIELD] else ""
        edits.append((start, end, raw[:closing] + separator + encoded_ref + raw[closing:]))
    else:
        closing = text.rfind("}")
        separator = "," if original else ""
        edits.append((closing, closing, separator + _json(ARCHIVE_FIELD) + ":" + "[" + encoded_ref + "]"))
    result = text
    for start, end, replacement in sorted(edits, reverse=True):
        result = result[:start] + replacement + result[end:]
    return result

def _url(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("archive URL must be an absolute HTTPS URL")
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.netloc or parts.username or parts.password or parts.fragment:
        raise ValueError("archive URL must be an absolute HTTPS URL without credentials or fragment")
    return value


@dataclass(frozen=True)
class ArchivePlan:
    archive_bytes: bytes
    compacted_manifest: str
    archive_reference: dict


def prepare_archive(manifest: str, archive_url: str) -> ArchivePlan | None:
    """Return deterministic archive and compacted payload, or None for an unchanged replay.

    The caller must durably upload and read back ``archive_bytes`` at ``archive_url``
    before applying ``compacted_manifest`` with an exact native preimage guard.
    """
    original = _parse(manifest)
    if not any(len(original.get(field, [])) > 1 for field in HISTORY_FIELDS):
        return None
    _url(archive_url)
    data = manifest.encode("utf-8")
    summaries = _summaries(manifest, original)
    ref = {"schema": SCHEMA, "archiveUrl": archive_url, "archiveSHA256": _sha(data),
           "originalEvidenceManifestSHA256": _sha(data), "arrays": summaries}
    compact_text = _compact(manifest, original, ref)
    plan = ArchivePlan(data, compact_text, ref)
    if restore_original(compact_text, data) != manifest:
        raise ValueError("archive did not reconstruct the exact preimage")
    return plan


def restore_original(compacted_manifest: str, archive_bytes: bytes) -> str:
    """Validate archive/reference/compaction and return the exact original manifest text."""
    compacted = _parse(compacted_manifest)
    refs = compacted.get(ARCHIVE_FIELD)
    if not refs or not isinstance(refs[-1], dict):
        raise ValueError("missing archive reference")
    ref = refs[-1]
    if ref.get("schema") != SCHEMA:
        raise ValueError("unsupported archive reference")
    _url(ref.get("archiveUrl"))
    if not isinstance(archive_bytes, bytes) or _sha(archive_bytes) != ref.get("archiveSHA256"):
        raise ValueError("archive hash mismatch")
    if _sha(archive_bytes) != ref.get("originalEvidenceManifestSHA256"):
        raise ValueError("preimage hash mismatch")
    try:
        text = archive_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("archive is not UTF-8") from exc
    original = _parse(text)
    if ref.get("arrays") != _summaries(text, original):
        raise ValueError("archive array metadata mismatch")
    if compacted_manifest != _compact(text, original, ref):
        raise ValueError("compacted manifest differs from the permitted change")
    return text
