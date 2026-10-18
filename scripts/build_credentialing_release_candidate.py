"""Build an immutable credentialing release candidate from reviewed repositories.

The script resolves public Git repository references and writes a candidate
receipt. It does not modify a repository, deploy a tenant, publish data or
promote the candidate into an approved release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict, cast
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "portfolio" / "credentialing-release-sources.json"
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_MVP_MODULES = {
    "careops-approve",
    "careops-decisions",
    "careops-process",
    "careops-legacy-migration",
}


class RepositorySource(TypedDict, total=False):
    """One versioned repository source."""

    id: str
    repository: str
    ref: str
    role: str
    requiredForMvp: bool
    repositoryRenamePending: str


class ResolvedSource(TypedDict):
    """One immutable source included in a candidate."""

    repository: str
    ref: str
    commit: str
    role: str
    required_for_mvp: bool


class Candidate(TypedDict):
    """Machine-readable release candidate."""

    schema_version: int
    release_family: str
    status: str
    observed_at: str
    source_collections: dict[str, ResolvedSource]
    modules: dict[str, ResolvedSource]
    changed_from_baseline: list[str]
    validation_gates: dict[str, bool]
    production_writes: bool
    evidence_ceiling: str


def load_object(path: Path) -> dict[str, object]:
    """Load one JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        message = f"Expected JSON object: {path}"
        raise TypeError(message)
    return cast("dict[str, object]", value)


def validate_repository_url(value: str) -> None:
    """Restrict release discovery to public HTTPS GitHub repositories."""
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        message = f"Repository must use public HTTPS GitHub: {value}"
        raise ValueError(message)
    if not parsed.path.endswith(".git"):
        message = f"Repository URL must end in .git: {value}"
        raise ValueError(message)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        message = f"Repository URL must not contain credentials or query data: {value}"
        raise ValueError(message)


def validate_ref(value: str) -> None:
    """Allow reviewed branch or tag refs only."""
    if not value.startswith(("refs/heads/", "refs/tags/")):
        message = f"Unsupported Git ref: {value}"
        raise ValueError(message)
    if any(character.isspace() for character in value):
        message = f"Git ref contains whitespace: {value}"
        raise ValueError(message)


def resolve_git_ref(repository: str, reference: str) -> str:
    """Resolve one public Git reference to an immutable commit."""
    validate_repository_url(repository)
    validate_ref(reference)
    completed = subprocess.run(
        ["git", "ls-remote", "--exit-code", repository, reference],
        check=True,
        capture_output=True,
        text=True,
        timeout=45,
    )
    matches = set()
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == reference:
            matches.add(parts[0])
    if len(matches) != 1:
        message = f"Expected one immutable commit for {repository} {reference}"
        raise ValueError(message)
    commit = matches.pop()
    if COMMIT_PATTERN.fullmatch(commit) is None:
        message = f"Invalid commit returned for {repository} {reference}"
        raise ValueError(message)
    return commit


def load_sources(value: object, field: str) -> list[RepositorySource]:
    """Validate a registry source list."""
    if not isinstance(value, list):
        message = f"{field} must be an array"
        raise TypeError(message)
    sources: list[RepositorySource] = []
    for item in cast("list[object]", value):
        if not isinstance(item, dict):
            message = f"Every {field} entry must be an object"
            raise TypeError(message)
        source = cast("RepositorySource", item)
        for required in ("id", "repository", "ref", "role"):
            if not isinstance(source.get(required), str) or not source[required].strip():
                message = f"{field} entry is missing {required}"
                raise ValueError(message)
        validate_repository_url(source["repository"])
        validate_ref(source["ref"])
        sources.append(source)
    identifiers = [source["id"] for source in sources]
    if len(identifiers) != len(set(identifiers)):
        message = f"{field} identifiers must be unique"
        raise ValueError(message)
    return sources


def baseline_commits(path: Path | None) -> dict[str, str]:
    """Read module commits from an optional prior release manifest."""
    if path is None:
        return {}
    baseline = load_object(path)
    modules = baseline.get("modules", {})
    if not isinstance(modules, dict):
        return {}
    commits: dict[str, str] = {}
    for module_id, value in cast("dict[object, object]", modules).items():
        if not isinstance(module_id, str) or not isinstance(value, dict):
            continue
        commit = cast("dict[str, object]", value).get("commit")
        if isinstance(commit, str):
            commits[module_id] = commit
    return commits


def resolve_sources(
    sources: list[RepositorySource],
    resolver: Callable[[str, str], str],
) -> dict[str, ResolvedSource]:
    """Resolve reviewed sources to immutable commits."""
    resolved: dict[str, ResolvedSource] = {}
    for source in sources:
        commit = resolver(source["repository"], source["ref"])
        if COMMIT_PATTERN.fullmatch(commit) is None:
            message = f"Resolver returned invalid commit for {source['id']}"
            raise ValueError(message)
        resolved[source["id"]] = {
            "repository": source["repository"],
            "ref": source["ref"],
            "commit": commit,
            "role": source["role"],
            "required_for_mvp": bool(source.get("requiredForMvp", False)),
        }
    return resolved


def build_candidate(
    registry: dict[str, object],
    *,
    observed_at: str,
    resolver: Callable[[str, str], str] = resolve_git_ref,
    baseline: dict[str, str] | None = None,
) -> Candidate:
    """Build a non-promoted immutable release candidate."""
    if registry.get("schemaVersion") != 1:
        message = "Unsupported release-source registry version"
        raise ValueError(message)
    if registry.get("productionWrites") is not False:
        message = "Release-source registry must prohibit production writes"
        raise ValueError(message)
    parsed_observed_at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    if parsed_observed_at.tzinfo is None:
        message = "observed_at must include a timezone"
        raise ValueError(message)

    source_collections = load_sources(
        registry.get("sourceCollections"),
        "sourceCollections",
    )
    modules = load_sources(registry.get("modules"), "modules")
    module_ids = {source["id"] for source in modules}
    if not REQUIRED_MVP_MODULES <= module_ids:
        message = "Required credentialing MVP modules are missing"
        raise ValueError(message)
    if not all(
        source.get("requiredForMvp") is True
        for source in modules
        if source["id"] in REQUIRED_MVP_MODULES
    ):
        message = "Every core credentialing module must be required for the MVP"
        raise ValueError(message)

    resolved_collections = resolve_sources(source_collections, resolver)
    resolved_modules = resolve_sources(modules, resolver)
    baseline_values = baseline or {}
    changed = sorted(
        module_id
        for module_id, source in resolved_modules.items()
        if baseline_values.get(module_id) != source["commit"]
    )
    return {
        "schema_version": 1,
        "release_family": str(registry["releaseFamily"]),
        "status": "candidate-not-validated",
        "observed_at": parsed_observed_at.astimezone(UTC).isoformat().replace(
            "+00:00",
            "Z",
        ),
        "source_collections": resolved_collections,
        "modules": resolved_modules,
        "changed_from_baseline": changed,
        "validation_gates": {
            "immutable_checkout": False,
            "cross_module_contracts": False,
            "synthetic_negative_paths": False,
            "source_currentness_and_rights": False,
            "human_release_approval": False,
        },
        "production_writes": False,
        "evidence_ceiling": (
            "Observed public repository heads and candidate diffs only. This is not an "
            "approved release, policy approval, deployment, migration, credentialing "
            "decision, register activation or operating-effectiveness finding."
        ),
    }


def sha256(path: Path) -> str:
    """Return the SHA-256 digest for one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def main() -> int:
    """Resolve sources and write a reviewable candidate and receipt."""
    args = parse_args()
    candidate = build_candidate(
        load_object(args.registry),
        observed_at=args.observed_at,
        baseline=baseline_commits(args.baseline),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema_version": 1,
        "candidate_sha256": sha256(args.output),
        "candidate_path": args.output.name,
        "module_count": len(candidate["modules"]),
        "source_collection_count": len(candidate["source_collections"]),
        "changed_from_baseline": candidate["changed_from_baseline"],
        "passed": True,
        "evidence_ceiling": candidate["evidence_ceiling"],
    }
    if args.receipt is not None:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(receipt, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
