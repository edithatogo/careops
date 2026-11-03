# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Pre-transfer private-destination and Presidio gate; diagnostics contain no raw data."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "careops_presidio_scan", HERE / "presidio_scan.py"
)
SCAN = importlib.util.module_from_spec(SPEC)
try:
    SPEC.loader.exec_module(SCAN)
except Exception:  # noqa: BLE001 -- unavailable helper must not disclose a traceback
    print("CareOps push blocked: trusted scanner unavailable.", file=sys.stderr)
    raise SystemExit(1)
OID, Refusal, git, selected_text = SCAN.OID, SCAN.Refusal, SCAN.git, SCAN.selected_text
ZERO = "0" * 40


def run(command: list[str], *, data: bytes | None = None, timeout: int = 60) -> bytes:
    result = subprocess.run(
        command, input=data, capture_output=True, check=False, timeout=timeout
    )
    if result.returncode:
        raise Refusal("required_command_failed")
    return result.stdout


def destination(url: str, policy: dict, command=run, *, advertise=True) -> list[str]:
    """Only the approved repository; no credentials, query, fragments or alternate host."""
    repo = policy["repository"]
    permitted = {
        f"https://github.com/{repo}",
        f"https://github.com/{repo}.git",
        f"git@github.com:{repo}",
        f"git@github.com:{repo}.git",
    }
    if (
        policy["host"] != "github.com"
        or policy["requiredVisibility"] != "PRIVATE"
        or url not in permitted
    ):
        raise Refusal("destination_not_approved")
    state = json.loads(
        command(["gh", "api", "--hostname", "github.com", "repos/" + repo])
    )
    if (
        state.get("full_name", "").lower() != repo.lower()
        or state.get("private") is not True
        or state.get("visibility") != "private"
    ):
        raise Refusal("private_visibility_not_verified")
    if not advertise:
        return []  # CI uses its explicit fetched range, without Git transport credentials.
    refs = command(["git", "ls-remote", "--heads", url])
    if len(refs) > 2 * 1024 * 1024:
        raise Refusal("remote_scope_limit")
    tips = []
    for line in refs.decode().splitlines():
        parts = line.split()
        if (
            len(parts) != 2
            or not OID.fullmatch(parts[0])
            or not parts[1].startswith("refs/heads/")
        ):
            raise Refusal("invalid_remote_metadata")
        tips.append(parts[0])
    return sorted(set(tips))


def push_rows(payload: bytes) -> list[tuple[str, str]]:
    if len(payload) > 1024 * 1024:
        raise Refusal("push_scope_limit")
    rows = []
    for line in payload.decode().splitlines():
        fields = line.split()
        if len(fields) != 4 or any(
            not OID.fullmatch(v) for v in [fields[1], fields[3]]
        ):
            raise Refusal("invalid_push_metadata")
        if not fields[2].startswith("refs/heads/"):
            raise Refusal("non_branch_push_requires_review")
        if fields[1] != ZERO:
            rows.append((fields[1], fields[3]))
    return rows


def scanner(root: Path, items: list[dict], policy: dict, command=run) -> None:
    python = root / ".venv-careops-presidio/bin/python"
    if not python.is_file() or python.parent.parent.is_symlink():
        raise Refusal("presidio_runtime_missing")
    reviews = json.loads((HERE / "presidio-reviewed-findings.json").read_text())
    policy_hash = hashlib.sha256(
        (HERE / "presidio-policy.json").read_bytes()
    ).hexdigest()
    if (
        reviews.get("schemaVersion") != 1
        or reviews.get("policy_sha256") != policy_hash
        or not isinstance(reviews.get("findings"), list)
    ):
        raise Refusal("text_review_policy_changed")
    payload = json.dumps(
        {
            "policy": policy,
            "items": items,
            "reviews": reviews,
            "expected_prefix": str(python.parent.parent),
        }
    ).encode()
    result = json.loads(
        command(
            [str(python), "-I", str(HERE / "presidio_scan.py")],
            data=payload,
            timeout=300,
        )
    )
    if (
        result.get("protocol") != 1
        or result.get("error")
        or result.get("checked") != len(items)
        or not isinstance(result.get("findings"), list)
    ):
        raise Refusal("presidio_scan_not_verified")
    if result["findings"]:
        raise Refusal("presidio_personal_details_detected")


def notify() -> None:
    """Generic local owner notification only. Its success never controls permission to push."""
    if (
        sys.platform == "darwin"
        and not os.environ.get("CI")
        and not os.environ.get("CAREOPS_NOTIFICATION_WRAPPED")
    ):
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'display notification "Push blocked. Review the local privacy gate." with title "CareOps privacy"',
                ],
                capture_output=True,
                check=False,
                timeout=3,
            )
        except (OSError, subprocess.SubprocessError):
            print(
                "Local notification unavailable; push remains blocked.", file=sys.stderr
            )


def main() -> int:
    class SilentParser(argparse.ArgumentParser):
        def error(self, _message):
            raise Refusal("invalid_gate_arguments")

    parser = SilentParser(description=__doc__)
    parser.add_argument("remote", nargs="?")
    parser.add_argument("url", nargs="?")
    parser.add_argument(
        "--legacy", help="Installed managed dispatcher retained verbatim"
    )
    parser.add_argument("--ci-base")
    parser.add_argument("--ci-tip")
    args = parser.parse_args()
    try:
        policy = json.loads((HERE / "presidio-policy.json").read_text())
        root = Path(
            run(["git", "rev-parse", "--show-toplevel"]).decode().strip()
        ).resolve()
        if git(root, "rev-parse", "--is-shallow-repository").strip() != b"false":
            raise Refusal("complete_history_required")
        # Network metadata preflight precedes analysis. No source text leaves this process tree.
        if args.ci_tip:
            if os.environ.get("GITHUB_REPOSITORY") != policy["repository"]:
                raise Refusal("ci_repository_not_approved")
            destination(
                "https://github.com/" + policy["repository"] + ".git",
                policy,
                advertise=False,
            )
            if (
                not args.ci_base
                or not OID.fullmatch(args.ci_base)
                or not OID.fullmatch(args.ci_tip)
            ):
                raise Refusal("explicit_ci_range_required")
            rows, known, payload = [(args.ci_tip, args.ci_base)], [args.ci_base], b""
        else:
            if not args.remote or not args.url:
                raise Refusal("explicit_destination_required")
            # URL rewriting can route a seemingly approved URL to another server.
            rewrite = subprocess.run(
                [
                    "git",
                    "config",
                    "--get-regexp",
                    r"^url\..*\.(insteadof|pushinsteadof)$",
                ],
                capture_output=True,
                check=False,
            )
            if rewrite.returncode != 1:
                raise Refusal("unreviewed_transport_rewrite")
            known = destination(args.url, policy)
            payload = sys.stdin.buffer.read(1024 * 1024 + 1)
            rows = push_rows(payload)
        bases = []
        for oid in known:
            try:
                if git(root, "cat-file", "-t", oid).strip() == b"commit":
                    bases.append(oid)
            except Refusal:
                pass  # Never exclude an unknown object; conservative full scan instead.
        items, identities, total = [], set(), 0
        for tip, _old in rows:
            for item in selected_text(root, tip, bases, policy):
                if item["identity"] in identities:
                    continue
                identities.add(item["identity"])
                total += len(item["text"].encode())
                if total > policy["maxTotalBytes"] or len(items) >= policy["maxBlobs"]:
                    raise Refusal("combined_text_scope_limit")
                items.append(item)
        # Even a clean/deletion-only push must prove scanner and model availability.
        scanner(root, items, policy)
        if args.legacy:
            run(
                [sys.executable, "-I", args.legacy, "pre-push", args.remote, args.url],
                data=payload,
                timeout=600,
            )
        elif not args.ci_tip:
            for tip, old in rows:
                selection = tip if old == ZERO else old + ".." + tip
                run(
                    [
                        "gitleaks",
                        "git",
                        ".",
                        "--log-opts=" + selection,
                        "--gitleaks-ignore-path",
                        str(HERE / "gitleaks-reviewed.ignore"),
                        "--ignore-gitleaks-allow",
                        "--redact",
                        "--no-banner",
                    ],
                    timeout=300,
                )
                command = [
                    sys.executable,
                    "-I",
                    str(HERE / "check.py"),
                    "--revision",
                    tip,
                ]
                run(
                    command + (["--history"] if old == ZERO else ["--base", old]),
                    timeout=600,
                )
        print("CareOps private destination and offline Presidio gate passed.")
        return 0
    except Exception:  # noqa: BLE001 -- privacy boundary; arbitrary raw errors must not escape
        # No exception, filename, URL, subprocess stderr, match or snippet is echoed.
        print(
            "CareOps push blocked: private destination or complete privacy scan not verified.",
            file=sys.stderr,
        )
        notify()
        return 1


if __name__ == "__main__":
    try:
        code = main()
    except Exception:  # noqa: BLE001 -- startup failure is a refusal, never a bypass
        print("CareOps push blocked: privacy gate could not start.", file=sys.stderr)
        notify()
        code = 1
    raise SystemExit(code)
