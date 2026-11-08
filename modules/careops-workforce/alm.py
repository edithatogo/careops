# SPDX-License-Identifier: Apache-2.0
"""Verify the reviewed public tree and prepare a private environment derivative."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
LOCK = "source-lock.json"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory():
    files = {}
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            raise ValueError(f"Unexpected link: {relative}")
        if path.is_file() and relative.as_posix() != LOCK:
            files[relative.as_posix()] = digest(path)
    return files


def verify():
    expected = json.loads((ROOT / LOCK).read_text())
    if inventory() != expected:
        raise ValueError("Public tree differs from the reviewed source inventory")
    for name in expected:
        if not name.startswith(("Workforce.Report/", "Workforce.SemanticModel/")):
            continue
        text = (ROOT / name).read_text(encoding="utf-8")
        if re.search(r'Binary\.FromText|DATATABLE\s*\(|data:.*base64|/(?:Users|Volumes)/|sharepoint\.com|powerbi://|[\w.+-]+@[\w.-]+\.[a-z]{2,}', text, re.I):
            raise ValueError(f"Embedded payload or private binding in {name}")
    print(f"Verified {len(expected)} reviewed source files")


def bind(config, feed, output):
    spec = json.loads(config.read_text())
    site, folder = spec["source_site"], spec["source_folder"]
    url = urlsplit(site)
    if (spec["stage"] not in ("development", "test", "production")
            or url.scheme != "https" or not (url.hostname or "").endswith(".sharepoint.com")
            or url.username or url.password or url.query or url.fragment
            or not re.fullmatch(r"[\w -]+", folder)):
        raise ValueError("Invalid private environment configuration")
    schema = json.loads((ROOT / "feed-schema.json").read_text())
    hashes = {}
    for name, header in schema.items():
        path = feed / name
        with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
            if next(csv.reader(stream)) != next(csv.reader([header])):
                raise ValueError(f"Source header mismatch: {name}")
        hashes[name] = digest(path)
    if hashes != spec["sha256"]:
        raise ValueError("Private source manifest differs from the selected feed")
    if output.resolve().is_relative_to(ROOT):
        raise ValueError("Private build must be outside the public tree")
    output.mkdir(mode=0o700)
    for name in ("Workforce.Report", "Workforce.SemanticModel"):
        shutil.copytree(ROOT / name, output / name)
    shutil.copyfile(ROOT / "Workforce.pbip", output / "Workforce.pbip")
    expr = output / "Workforce.SemanticModel/definition/expressions.tmdl"
    text = expr.read_text()
    for key, value in (("Source Site", site), ("Source Folder", folder)):
        text = text.replace(f"expression '{key}' = \"\"", f"expression '{key}' = " + '"' + value.replace('"', '""') + '"')
    expr.write_text(text)
    (output / "binding-receipt.json").write_text(json.dumps({
        "stage": spec["stage"], "source_lock_sha256": digest(ROOT / LOCK),
        "feed_sha256": hashes,
    }, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", nargs=3, type=Path, metavar=("CONFIG", "FEED", "OUTPUT"))
    args = parser.parse_args()
    verify()
    if args.bind:
        bind(*args.bind)
