"""Deterministic, offline engineering context and CI-readiness preflight.

This source-only preflight DOES NOT intercept external tools, sandbox an agent,
authorize deployment, or certify a hosted run. It emits content-free references
and refuses unknown capabilities. Use the host's independent permission boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

COMMIT = re.compile(r"[0-9a-f]{40}\Z")
TASK = re.compile(r"[A-Z0-9][A-Z0-9_.-]{0,60}\Z")
ALLOWED_TOOLS = frozenset({"repo:read", "runner:focused-test"})
CONTEXT_NAMES = ("AGENTS.md", "conductor/index.md",
                 "docs/targeted-testing.md", "portfolio/repos.json")
TEST_TARGETS = {
    "portfolio-scripts/engineering_frontier.py": ("test_engineering_frontier.py", "test_frontier_gateway.py"),
    "portfolio-scripts/frontier_gateway.py": ("test_frontier_gateway.py",),
    "portfolio-scripts/run_tests.py": ("test_test_selection.py",),
    "portfolio-scripts/ci_delivery.py": ("test_ci_delivery.py",),
}


class FrontierError(ValueError):
    """Safe error class: never include untrusted source content or credentials."""


def _git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(root), *args],
                              check=True, capture_output=True, timeout=12).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise FrontierError("source-read-failed") from exc


def _safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise FrontierError("invalid-path")
    p = PurePosixPath(value)
    if (p.is_absolute() or value != p.as_posix() or
            any(part in {".", "..", ".git"} for part in value.split("/")) or
            any(ord(ch) < 32 for ch in value)):
        raise FrontierError("invalid-path")
    return value


def _components(root: Path) -> list[dict[str, str]]:
    try:
        data = json.loads(_git(root, "show", "HEAD:portfolio/repos.json").decode("utf-8"))
        components = data["components"]
        if not isinstance(components, list):
            raise ValueError()
        return components
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise FrontierError("source-registry-unavailable") from exc


def resolve_owner(path: str, root: Path) -> str:
    path = _safe_path(path)
    candidates = []
    for item in _components(root):
        prefix = _safe_path(item["path"])
        if path == prefix or path.startswith(prefix + "/"):
            candidates.append((len(prefix), item))
    if not candidates:
        if path.startswith("modules/") or path.startswith("careops-"):
            raise FrontierError("unknown-module")
        return "careops"
    top = sorted(candidates, key=lambda x: x[0], reverse=True)[0][1]
    if top.get("materialization") != "integrated-source":
        raise FrontierError("optional-submodule-needs-separate-qualified-checkout")
    return str(top["name"])


def _tree(root: Path, sha: str) -> dict[str, tuple[str, str]]:
    entries = {}
    for record in _git(root, "ls-tree", "-rz", "--full-tree", sha).split(b"\0"):
        if not record:
            continue
        try:
            meta, path = record.split(b"\t", 1)
            mode, kind, blob = meta.decode("ascii").split()
            name = path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise FrontierError("source-index-invalid") from exc
        entries[name] = (mode, blob)
    return entries


def _blob_hash(root: Path, oid: str) -> str:
    value = _git(root, "cat-file", "blob", oid)
    if len(value) > 131072:
        raise FrontierError("context-too-large")
    return hashlib.sha256(value).hexdigest()


def guard_tool(operation: str, granted: set[str] | frozenset[str]) -> bool:
    """Preflight only; a separate tool server must enforce its own permissions."""
    if operation not in ALLOWED_TOOLS or operation not in granted:
        raise FrontierError("tool-denied")
    return True


def build_packet(root: Path, task_id: str, sha: str, paths: list[str]) -> dict[str, Any]:
    root = root.resolve()
    if not isinstance(task_id, str) or not TASK.fullmatch(task_id):
        raise FrontierError("invalid-task")
    if not isinstance(sha, str) or not COMMIT.fullmatch(sha):
        raise FrontierError("invalid-source-sha")
    if _git(root, "rev-parse", "HEAD").decode().strip() != sha:
        raise FrontierError("stale-source")
    if not paths or len(paths) != len(set(paths)):
        raise FrontierError("empty-or-duplicate-paths")
    selected = [_safe_path(p) for p in paths]
    owners = {resolve_owner(p, root) for p in selected}
    if len(owners) != 1:
        raise FrontierError("cross-module-task")
    owner = next(iter(owners))
    tree = _tree(root, sha)
    for path in selected:
        if path not in tree:
            raise FrontierError("not-tracked")
        mode, _ = tree[path]
        if (mode not in {"100644", "100755"} or
                (root / path).is_symlink() or not (root / path).is_file()):
            raise FrontierError("unsafe-file")
    context_paths = list(CONTEXT_NAMES)
    candidates = [c for c in _components(root) if c.get("name") == owner]
    if candidates:
        context_paths.append(candidates[0]["path"] + "/AGENTS.md")
    context = []
    for name in context_paths:
        if name in tree:
            mode, oid = tree[name]
            if mode != "100644" or (root / name).is_symlink():
                raise FrontierError("unsafe-context")
            context.append({"path": name, "sha256": _blob_hash(root, oid)})
        elif name in {"AGENTS.md", "portfolio/repos.json"}:
            raise FrontierError("missing-required-context")
    known = sorted({name for path in selected for name in TEST_TARGETS.get(path, ())})
    manual_selection = owner != "careops" or any(path not in TEST_TARGETS for path in selected)
    return {
        "schema_version": "1.0.0",
        "source": {"repository": "edithatogo/careops", "commit": sha},
        "task": {"id": task_id, "owner": owner, "scope": "read-test",
                 "changed_paths": sorted(selected),
                 "source_blobs": {p: tree[p][1] for p in sorted(selected)}},
        "context": context,
        "tools": {"allowed": sorted(ALLOWED_TOOLS), "denied_by_default": True,
                  "actual_tool_enforcement": False},
        "tests": {"selected": [f"portfolio-scripts/checks/{name}" for name in known],
                  "owner_selection_required": manual_selection, "full_release_gate_required": True},
        "qualification": {"level": "offline-source-plan", "native": False,
                          "hosted_ci": False, "operation_authorized": False}
    }


def check_required_contexts(sha: str, required: list[str], checks: list[dict]) -> dict[str, Any]:
    """Classify exact-head hosted check facts without claiming deployment or merge."""
    if (not isinstance(sha, str) or not COMMIT.fullmatch(sha) or
            not isinstance(required, list) or not required or
            not all(isinstance(name, str) and name for name in required) or
            len(required) != len(set(required)) or
            not isinstance(checks, list) or not all(isinstance(c, dict) for c in checks)):
        raise FrontierError("invalid-check-scope")
    by_name: dict[str, list[dict]] = {}
    for c in checks:
        if c.get("name") in required:
            by_name.setdefault(c["name"], []).append(c)
    unverified = []
    for name in required:
        rows = by_name.get(name, [])
        if len(rows) != 1:
            unverified.append(name + ":missing-or-duplicate")
            continue
        check = rows[0]
        if (check.get("head_sha") != sha or check.get("status") != "completed" or
                check.get("conclusion") != "success" or
                not check.get("started_at") or not check.get("completed_at")):
            unverified.append(name + ":not-qualified")
    return {"source_sha": sha, "required_count": len(required),
            "all_required_passed": not unverified, "unverified": unverified,
            "snapshot_input_verified": False, "protected_merge_qualified": False,
            "native_deployment_qualified": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="action", required=True)
    packet = sub.add_parser("packet", help="Generate content-free exact-SHA context packet")
    packet.add_argument("--task-id", required=True)
    packet.add_argument("--source-sha", required=True)
    packet.add_argument("--changed", action="append", required=True)
    checks = sub.add_parser("checks", help="Classify offline JSON check snapshot")
    checks.add_argument("--input", type=Path, required=True)
    try:
        args = parser.parse_args()
        if args.action == "packet":
            result = build_packet(args.root, args.task_id, args.source_sha, args.changed)
        else:
            record = json.loads(args.input.read_text(encoding="utf-8"))
            result = check_required_contexts(record["head_sha"], record["required"], record["checks"])
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (FrontierError, OSError, ValueError, KeyError, TypeError) as exc:
        # No source excerpts, credentials, annotations or fetched failure payloads.
        parser.exit(2, "Frontier preflight refused: " +
                    (str(exc) if isinstance(exc, FrontierError) else "invalid-input") + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
