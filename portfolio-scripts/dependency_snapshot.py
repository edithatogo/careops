"""Prepare a GitHub dependency snapshot from a reviewed uv CycloneDX export.

No network, dependency resolution, installation or submission is performed.
The initial contract covers public PyPI dependencies only, not artifact SBOMs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def snapshot(
    document: dict,
    *,
    sha: str,
    ref: str,
    manifest: str,
    job_id: str,
    correlator: str,
    scanned: str,
    inventory_only: bool = False,
) -> dict:
    require(bool(re.fullmatch(r"[a-f0-9]{40}", sha)), "Expected immutable source SHA")
    require(
        bool(re.fullmatch(r"refs/heads/[A-Za-z0-9][A-Za-z0-9._/-]*", ref))
        and ".." not in ref
        and not ref.endswith("/"),
        "Expected a branch ref",
    )
    require(
        bool(re.fullmatch(r"[A-Za-z0-9._-]{1,100}", job_id)), "Invalid job identity"
    )
    require(
        bool(re.fullmatch(r"[A-Za-z0-9_./:-]{1,160}", correlator)), "Invalid correlator"
    )
    path = PurePosixPath(manifest)
    require(
        not path.is_absolute()
        and ".." not in path.parts
        and bool(re.fullmatch(r"[A-Za-z0-9_./-]+", manifest))
        and (
            path.name == "uv.lock"
            or (inventory_only and path.suffix in (".lock", ".txt"))
        ),
        "Expected repository-relative dependency manifest",
    )
    require(
        scanned.endswith("Z")
        and datetime.fromisoformat(scanned).utcoffset().total_seconds() == 0,
        "Expected UTC scanned timestamp",
    )
    require(
        document.get("bomFormat") == "CycloneDX"
        and document.get("specVersion") == "1.5",
        "Expected CycloneDX 1.5 dependency export",
    )
    root = document["metadata"]["component"]["bom-ref"]
    components = document["components"]
    require(
        isinstance(root, str)
        and isinstance(components, list)
        and 0 < len(components) <= 10000,
        "Invalid dependency component set",
    )
    refs: dict[str, str] = {}
    for component in components:
        identity, purl = component["bom-ref"], component["purl"]
        require(
            isinstance(identity, str) and identity != root and identity not in refs,
            "Duplicate or conflicting component identity",
        )
        require(
            isinstance(purl, str)
            and bool(
                re.fullmatch(r"pkg:pypi/[a-z0-9][a-z0-9._-]*@[A-Za-z0-9_.!+%-]+", purl)
            ),
            "Only versioned public PyPI package URLs are supported",
        )
        distributions = [
            r
            for r in component.get("externalReferences", [])
            if r.get("type") == "distribution"
        ]
        require(
            inventory_only or bool(distributions),
            "Missing public distribution provenance",
        )
        for distribution in distributions:
            url = urlsplit(distribution["url"])
            require(
                url.scheme == "https"
                and url.hostname in ("files.pythonhosted.org", "pypi.org")
                and not url.username
                and not url.password
                and not url.query
                and not url.fragment
                and url.port in (None, 443),
                "Non-public distribution provenance",
            )
        refs[identity] = purl
    edges: dict[str, set[str]] = {}
    for entry in document["dependencies"]:
        identity = entry["ref"]
        require(identity == root or identity in refs, "Unresolved dependency node")
        require(identity not in edges, "Duplicate dependency node")
        dependencies = entry.get("dependsOn", [])
        require(
            isinstance(dependencies, list)
            and all(isinstance(v, str) and v in refs for v in dependencies),
            "Unresolved dependency edge",
        )
        edges[identity] = set(dependencies)
    require(root in edges and set(refs) <= set(edges), "Incomplete dependency graph")
    direct = {refs[v] for v in edges[root]}
    resolved: dict[str, dict] = {}
    for identity, purl in refs.items():
        item = resolved.setdefault(
            purl,
            {
                "package_url": purl,
                "relationship": "direct" if purl in direct else "indirect",
                "dependencies": [],
            },
        )
        item["dependencies"] = sorted(
            set(item["dependencies"]) | {refs[v] for v in edges[identity]}
        )
    if inventory_only:
        resolved = {purl: {"package_url": purl} for purl in resolved}
    return {
        "version": 0,
        "sha": sha,
        "ref": ref,
        "job": {"id": job_id, "correlator": correlator},
        "detector": {
            "name": "careops-pip-inspect-inventory"
            if inventory_only
            else "careops-uv-cyclonedx",
            "version": "1.0.0",
            "url": "https://github.com/edithatogo/careops",
        },
        "scanned": scanned,
        "manifests": {
            manifest: {
                "name": manifest,
                "file": {"source_location": manifest},
                "resolved": dict(sorted(resolved.items())),
            }
        },
    }


def pip_inventory(document: dict) -> dict:
    """Inventory actual installed tooling without inventing extras/edge semantics.

    pip inspect does not establish which extras were selected or public-index
    provenance. The caller must qualify the existing public hash lock and install.
    Local/VCS distributions are refused; installation locations never leave input.
    """
    require(document.get("version") == "1", "Expected pip inspect format 1")
    require(
        str(document["environment"]["python_version"]) == "3.15"
        and str(document["environment"]["python_full_version"]).startswith("3.15."),
        "Expected actual Python 3.15 inspection",
    )
    components = []
    seen = set()
    for item in document["installed"]:
        require(
            not item.get("direct_url"),
            "Local/VCS distributions require separate source qualification",
        )
        metadata = item["metadata"]
        name = re.sub(r"[-_.]+", "-", metadata["name"]).lower()
        version = metadata["version"]
        require(name not in seen, "Duplicate installed package identity")
        seen.add(name)
        components.append({"bom-ref": name, "purl": "pkg:pypi/" + name + "@" + version})
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "metadata": {"component": {"bom-ref": "__installed_tooling__"}},
        "components": components,
        "dependencies": [{"ref": "__installed_tooling__"}]
        + [{"ref": c["bom-ref"]} for c in components],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sbom", type=Path)
    source.add_argument("--pip-inspect", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    for option in ("sha", "ref", "manifest", "job-id", "correlator", "scanned"):
        parser.add_argument("--" + option, required=True)
    args = parser.parse_args()
    source_path = args.sbom or args.pip_inspect
    require(
        source_path.stat().st_size <= 10 * 1024 * 1024,
        "Dependency export exceeds size bound",
    )
    raw = source_path.read_bytes()
    document = json.loads(raw)
    if args.pip_inspect:
        document = pip_inventory(document)
    value = snapshot(
        document,
        sha=args.sha,
        ref=args.ref,
        manifest=args.manifest,
        job_id=args.job_id,
        correlator=args.correlator,
        scanned=args.scanned,
        inventory_only=bool(args.pip_inspect),
    )
    value["metadata"] = {
        "source_input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_contract": "installed-tooling-inventory-no-edge-or-extras-claims"
        if args.pip_inspect
        else "frozen-uv-export-selected-groups",
    }
    encoded = json.dumps(value, indent=2) + "\n"
    with args.output.open("x", encoding="utf-8") as output:
        output.write(encoded)
    print("Prepared dependency snapshot; no submission performed.")


if __name__ == "__main__":
    main()
