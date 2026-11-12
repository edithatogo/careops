"""Offline Power Automate solution safety inventory (no tenant calls).

Reads an exported ZIP without extracting it, reports connector uses and
hard-coded inclusion writes. Prints no personal URLs, source identities or data.
Intended to detect *candidates* for review, not prove native configuration.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

SCHEMA = "careops-rims.solution-audit/1"
STANDARD = {"shared_sharepointonline", "shared_onedriveforbusiness",
            "shared_excelonlinebusiness", "shared_office365",
            "shared_powerbi"}  # Power BI functionality/licence checked separately


def walk(node, path=""):
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk(v, path + "/" + k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + "/" + str(i))


def inspect_bytes(raw: bytes, filename: str):
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("invalid workflow object")
    content = json.dumps(obj)
    connectors = sorted(set(__import__("re").findall(r"shared_[a-z0-9_]+", content, flags=__import__("re").I)))
    forced_included = []
    for path, node in walk(obj):
        # Only assignments to SharePoint register item status count; a
        # reference to an Included label or read-only expression does not.
        for key, value in node.items():
            if key.startswith("item/") and value == "Included":
                forced_included.append({"json_path": path + "/" + key})
    return {"filename": filename, "sha256": hashlib.sha256(raw).hexdigest(),
            "connectors": connectors,
            "unclassified_connectors": [x for x in connectors if x not in STANDARD],
            "forced_inclusion_assignments": forced_included}


def audit_zip(filename):
    payload = Path(filename).read_bytes()
    results = []
    with zipfile.ZipFile(filename) as archive:
        entries = [n for n in archive.namelist() if n.startswith("Workflows/") and n.endswith(".json")]
        if len(entries) != len(set(entries)):
            raise ValueError("duplicate ZIP workflow names")
        for name in sorted(entries):
            info = archive.getinfo(name)
            if info.file_size > 10_000_000:
                raise ValueError("oversize workflow definition")
            results.append(inspect_bytes(archive.read(name), name.rsplit("/", 1)[-1]))
    return {"schema": SCHEMA, "solution_sha256": hashlib.sha256(payload).hexdigest(),
            "workflow_count": len(results),
            "forced_inclusion_count": sum(len(r["forced_inclusion_assignments"]) for r in results),
            "workflows": results, "assessment": "offline_only"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect a RIMS ZIP without tenant/network access")
    parser.add_argument("zip", help="unmanaged solution export (read-only)")
    args = parser.parse_args(argv)
    try:
        result = audit_zip(args.zip)
    except (OSError, zipfile.BadZipFile, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, "RIMS solution audit refused: " + str(exc) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
