"""Read tracked dependency declarations; never execute tools or read auth stores."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path


def inventory(root: Path) -> dict:
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], check=True, capture_output=True
    ).stdout
    files = []
    actions = []
    declarations = []
    for raw in tracked.split(b"\0"):
        if not raw:
            continue
        name = raw.decode("utf-8")
        path = root / name
        if not path.is_file() or path.is_symlink():
            continue
        manifest = path.name in {
            "package.json",
            "package-lock.json",
            "pyproject.toml",
            "uv.lock",
            "global.json",
            "dotnet-tools.json",
            ".python-version",
            ".node-version",
            ".nvmrc",
            "dependencies.lock.json",
            "powerplatform-tools.json",
        }
        manifest |= path.name.startswith("requirements") and path.suffix in {
            ".txt",
            ".lock",
            ".in",
        }
        manifest |= path.suffix in {".csproj", ".cdsproj"}
        workflow = name.startswith(".github/workflows/") and path.suffix in {
            ".yml",
            ".yaml",
        }
        if not manifest and not workflow:
            continue
        content = path.read_bytes()
        files.append(
            {
                "path": name,
                "sha256": hashlib.sha256(content).hexdigest(),
                "kind": "workflow" if workflow else "dependency-declaration",
            }
        )
        text = content.decode("utf-8")

        def record(package, version, ecosystem):
            # Never export registry URLs, local paths, credentials or arbitrary text.
            reference = str(version)
            if not re.fullmatch(r"[A-Za-z0-9._+<>=!~^*, |;()-]+", reference):
                reference = "non-version-reference; inspect privately"
            declarations.append(
                {
                    "path": name,
                    "package": package,
                    "version": reference,
                    "ecosystem": ecosystem,
                }
            )

        if path.name == "package.json":
            data = json.loads(text)
            for field in (
                "dependencies",
                "devDependencies",
                "peerDependencies",
                "optionalDependencies",
                "engines",
            ):
                for package, version in data.get(field, {}).items():
                    record(package, version, "runtime" if field == "engines" else "npm")
        elif path.name == "pyproject.toml":
            data = tomllib.loads(text)
            project = data.get("project", {})
            if "requires-python" in project:
                record("python", project["requires-python"], "runtime")
            groups = [
                project.get("dependencies", []),
                data.get("build-system", {}).get("requires", []),
            ]
            groups.extend(project.get("optional-dependencies", {}).values())
            groups.extend(data.get("dependency-groups", {}).values())
            for group in groups:
                for dependency in group:
                    if isinstance(dependency, str):
                        match = re.match(r"([A-Za-z0-9_.-]+)(.*)", dependency)
                        if match:
                            record(match[1], match[2].strip() or "unbounded", "pypi")
        elif path.name.startswith("requirements"):
            for line in text.splitlines():
                match = re.match(r"^([A-Za-z0-9_.-]+)([<>=!~].*?)(?:\s+\\)?$", line)
                if match:
                    record(match[1], match[2], "pypi")
        elif path.name in {".python-version", ".node-version", ".nvmrc"}:
            record(
                "python" if path.name == ".python-version" else "node",
                text.strip(),
                "runtime",
            )
        elif path.suffix in {".csproj", ".cdsproj"}:
            tree = ET.fromstring(text)
            for element in tree.iter():
                tag = element.tag.rsplit("}", 1)[-1]
                if tag == "PackageReference":
                    record(
                        element.get("Include", "unknown"),
                        element.get("Version", "centrally-managed"),
                        "nuget",
                    )
                elif tag in {"TargetFramework", "TargetFrameworkVersion"}:
                    record("dotnet-target", element.text or "unknown", "runtime")
        if workflow:
            for action, revision in re.findall(r"uses:\s*([\w./-]+)@([\w.+/-]+)", text):
                actions.append(
                    {
                        "path": name,
                        "action": action,
                        "revision": revision,
                        "immutable": bool(re.fullmatch(r"[0-9a-f]{40}", revision)),
                    }
                )
    return {
        "repository": root.name,
        "declarations": files,
        "dependencies": declarations,
        "actions": actions,
        "scope": "tracked source declarations only; installed tools, effective access and native runtime are not inferred",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "schemaVersion": 1,
                "repositories": [inventory(root) for root in args.root],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
