# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed inspection of a supplied offline source ZIP; never authorises publication."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import PurePosixPath
import stat
from zipfile import BadZipFile, ZipFile

PREFIX = "careops-workforce-app/"
MANIFEST = "SOURCE-MANIFEST.json"
MAX_FILES = 300
MAX_FILE_BYTES = 1_048_576
MAX_TOTAL_BYTES = 8_388_608


class AdmissionError(ValueError):
    """Archive is unsafe or its source manifest cannot be verified."""


def _safe_path(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        name.startswith(PREFIX) and name != PREFIX and not name.endswith("/")
        and not path.is_absolute()
        and not any(part in ("..", ".", "") for part in name.split("/"))
        and "\\" not in name and ":" not in name
    )


def inspect_archive(contents: bytes) -> dict:
    """Check exact membership, path safety, size, UTF-8 content and SHA256.

    Output contains only paths, lengths, hashes and gates; not source bytes.
    Licence, staff privacy and cloud acceptance remain separate.
    """
    if not isinstance(contents, bytes) or len(contents) > MAX_TOTAL_BYTES:
        raise AdmissionError("invalid or oversized archive")
    try:
        with ZipFile(BytesIO(contents)) as z:
            infos = z.infolist()
            if not 2 <= len(infos) <= MAX_FILES + 1:
                raise AdmissionError("unexpected archive entry count")
            names = [info.filename for info in infos]
            if len(set(names)) != len(names) or len({n.casefold() for n in names}) != len(names):
                raise AdmissionError("duplicate or case-colliding paths")
            if names.count(MANIFEST) != 1:
                raise AdmissionError("exactly one manifest required")
            total = 0
            for info in infos:
                if info.filename != MANIFEST and not _safe_path(info.filename):
                    raise AdmissionError("unsafe archive path")
                if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                    raise AdmissionError("directory or symlink not accepted")
                if info.file_size > MAX_FILE_BYTES or info.file_size < 0:
                    raise AdmissionError("oversized entry")
                total += info.file_size
                if total > MAX_TOTAL_BYTES:
                    raise AdmissionError("oversized uncompressed archive")
            manifest = json.loads(z.read(MANIFEST).decode("utf-8"))
            entries = manifest["contents"]
            if not isinstance(entries, list) or len(entries) != len(infos) - 1:
                raise AdmissionError("manifest membership mismatch")
            listed: set[str] = set()
            items: list[dict] = []
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                    raise AdmissionError("invalid manifest entry")
                path = entry["path"]
                name = PREFIX + path
                if not _safe_path(name) or name in listed or name not in names:
                    raise AdmissionError("invalid or duplicate listed path")
                listed.add(name)
                payload = z.read(name)
                if b"\x00" in payload:
                    raise AdmissionError("binary entry in source-only archive")
                try:
                    payload.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise AdmissionError("non-UTF-8 source entry") from exc
                digest = sha256(payload).hexdigest()
                if entry.get("sha256") != digest or entry.get("bytes") != len(payload):
                    raise AdmissionError("source hash or length mismatch")
                items.append({"path": path, "bytes": len(payload), "sha256": digest})
            if set(names) - {MANIFEST} != listed:
                raise AdmissionError("unlisted source entry")
            return {
                "integrity": "verified", "source_count": len(items),
                "archive_sha256": sha256(contents).hexdigest(),
                "items": sorted(items, key=lambda item: item["path"]),
                "publication_approved": False, "native_deployment_qualified": False,
                "remaining_gates": [
                    "full_licence_review", "privacy_and_secret_scan",
                    "native_solution_reconstruction",
                    "authorised_tenant_readback", "industrial_rule_adoption",
                ],
            }
    except (BadZipFile, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise AdmissionError("unreadable or malformed source archive") from exc
