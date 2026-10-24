"""Build a deterministic reviewed Incidents source package and matching SPDX SBOM.

This publishes no data, private history, native deployment or operational acceptance.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], stderr=subprocess.PIPE
    )


def build(root: Path, destination: Path) -> dict:
    commit = git(root, "rev-parse", "HEAD").decode().strip()
    timestamp = int(git(root, "show", "-s", "--format=%ct", commit))
    inventory = json.loads(git(root, "show", commit + ":PUBLIC_SOURCE_FILES.json"))
    prefix = "modules/careops-incidents/"
    names = sorted(name for name in inventory["files"] if name.startswith(prefix))
    if not names or prefix.rstrip("/") in inventory["gitlinks"]:
        raise ValueError("Release requires integrated reviewed module source.")
    files = []
    for name in names:
        relative = name.removeprefix(prefix)
        path = PurePosixPath(relative)
        if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
            raise ValueError("Unsafe package path.")
        entry = git(root, "ls-tree", commit, "--", name).decode().split()
        if not entry or entry[0] not in ["100644", "100755"]:
            raise ValueError("Only reviewed regular source files can be packaged.")
        data = git(root, "show", commit + ":" + name)
        if b"\0" in data:
            raise ValueError("Binary content requires separate release qualification.")
        data.decode("utf-8")
        files.append((relative, data, int(entry[0], 8) & 0o777))
    if not {"LICENSE", "README.md", "SOURCE_PROVENANCE.json"} <= {f[0] for f in files}:
        raise ValueError(
            "Missing standalone source licence, instructions or provenance."
        )
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / ("careops-incidents-source-" + commit[:12] + ".tar.gz")
    sbom_path = destination / "careops-incidents.spdx.json"
    receipt_path = destination / "source-release.json"
    if any(
        p.exists()
        for p in [archive, sbom_path, receipt_path, destination / "SHA256SUMS"]
    ):
        raise ValueError(
            "Release output already exists; preserve the previous artifact."
        )
    with (
        archive.open("wb") as handle,
        gzip.GzipFile(filename="", mode="wb", fileobj=handle, mtime=0) as compressed,
        tarfile.open(fileobj=compressed, mode="w") as tar,
    ):
        for relative, data, mode in files:
            item = tarfile.TarInfo("careops-incidents/" + relative)
            item.size, item.mode, item.mtime = len(data), mode, timestamp
            item.uid = item.gid = 0
            item.uname = item.gname = ""
            tar.addfile(item, io.BytesIO(data))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    package_id = "SPDXRef-Package-CareOpsIncidentsSource"
    spdx_files, relationships, sha1s = [], [], []
    for relative, data, _ in files:
        file_id = "SPDXRef-File-" + hashlib.sha256(relative.encode()).hexdigest()
        # SPDX 2.3 requires SHA1 for its package-verification algorithm; SHA256
        # remains the release/content-integrity algorithm.
        sha1 = hashlib.sha1(data, usedforsecurity=False).hexdigest()
        sha1s.append(sha1)
        spdx_files.append(
            {
                "SPDXID": file_id,
                "fileName": "./careops-incidents/" + relative,
                "checksums": [
                    {
                        "algorithm": "SHA256",
                        "checksumValue": hashlib.sha256(data).hexdigest(),
                    },
                    {"algorithm": "SHA1", "checksumValue": sha1},
                ],
                "licenseConcluded": "NOASSERTION",
                "copyrightText": "NOASSERTION",
            }
        )
        relationships.append(
            {
                "spdxElementId": package_id,
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": file_id,
            }
        )
    verification = hashlib.sha1(
        "".join(sorted(sha1s)).encode(), usedforsecurity=False
    ).hexdigest()
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": archive.name,
        "documentNamespace": "https://spdx.org/spdxdocs/careops-incidents-" + commit,
        "creationInfo": {
            "creators": ["Tool: CareOps-source-release-builder"],
            "created": datetime.fromtimestamp(timestamp, UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
        "packages": [
            {
                "SPDXID": package_id,
                "name": "careops-incidents-source",
                "versionInfo": commit,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": True,
                "packageVerificationCode": {
                    "packageVerificationCodeValue": verification
                },
                "checksums": [{"algorithm": "SHA256", "checksumValue": digest}],
                "licenseConcluded": "Apache-2.0",
                "licenseDeclared": "Apache-2.0",
                "copyrightText": "NOASSERTION",
                "sourceInfo": "Reviewed standalone source module in edithatogo/careops at "
                + commit,
            }
        ],
        "files": spdx_files,
        "relationships": [
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": package_id,
            }
        ]
        + relationships,
    }
    sbom_path.write_text(json.dumps(sbom, indent=2) + "\n")
    receipt = {
        "schemaVersion": 1,
        "repository": "edithatogo/careops",
        "sourceCommit": commit,
        "module": "careops-incidents",
        "scope": "reviewed-standalone-source-only",
        "fileCount": len(files),
        "archive": archive.name,
        "sha256": digest,
        "sbom": sbom_path.name,
        "sbomSha256": hashlib.sha256(sbom_path.read_bytes()).hexdigest(),
        "nativeDeploymentQualified": False,
        "runtimeDependencies": "Python standard library; optional PowerShell/Power BI prerequisites not redistributed",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    (destination / "SHA256SUMS").write_text(
        digest
        + "  "
        + archive.name
        + "\n"
        + receipt["sbomSha256"]
        + "  "
        + sbom_path.name
        + "\n"
    )
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(Path(__file__).resolve().parents[1], args.output)
    print(json.dumps(result, indent=2))
