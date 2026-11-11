# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed *public CI* source-range Presidio check, separate from private pre-push.

Never authorises a Git push or waives the existing private-destination policy.
The CI caller already performs exact-range Gitleaks and source-inventory checks.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("careops_private_push_support", HERE / "pre_push.py")
if _SPEC is None or _SPEC.loader is None:
    raise SystemExit("Public CI privacy support unavailable")
pre_push = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pre_push)

OID = pre_push.OID
Refusal = pre_push.Refusal


def classify_refusal(error: Refusal) -> str:
    """Give CI only a fixed failure category; never show raw evidence or text."""
    categories = {
        "presidio_personal_details_detected": "unreviewed_semantic_findings",
        "text_scope_limit": "source_scope_limit",
        "blob_limit": "source_scope_limit",
        "commit_limit": "source_scope_limit",
        "combined_text_scope_limit": "source_scope_limit",
        "source_scope_limit": "source_scope_limit",
        "not_approved_public_ci_context": "repository_identity_invalid",
        "invalid_ci_revision": "source_range_invalid",
        "unqualified_local_checkout": "source_range_invalid",
        "missing_source_commit": "source_range_invalid",
        "presidio_scan_not_verified": "scanner_unavailable",
        "presidio_runtime_missing": "scanner_unavailable",
        "required_command_failed": "scanner_unavailable",
    }
    return categories.get(str(error), "verification_unavailable")


def validate_context(policy: dict, state: dict, environ: dict) -> None:
    """Require exact public source repository in trusted ordinary CI context."""
    expected = policy.get("repository")
    if (
        policy.get("host") != "github.com"
        or policy.get("requiredVisibility") != "PRIVATE"
        or not isinstance(expected, str)
        or expected != "edithatogo/careops"
        or environ.get("GITHUB_ACTIONS") != "true"
        or environ.get("GITHUB_REPOSITORY") != expected
        or environ.get("GITHUB_EVENT_NAME")
        not in {"push", "pull_request", "workflow_dispatch"}
        or not isinstance(state, dict)
        or state.get("full_name") != expected
        or state.get("private") is not False
        or state.get("visibility") != "public"
    ):
        raise Refusal("not_approved_public_ci_context")


def verify_range(base: str, tip: str, policy: dict) -> None:
    """Scan every selected outgoing source/commit message using offline Presidio."""
    if (
        not isinstance(base, str) or not isinstance(tip, str)
        or OID.fullmatch(base) is None or OID.fullmatch(tip) is None
        or base == pre_push.ZERO or tip == pre_push.ZERO
    ):
        raise Refusal("invalid_ci_revision")
    root = Path(
        pre_push.run(["git", "rev-parse", "--show-toplevel"]).decode().strip()
    ).resolve()
    if (
        pre_push.git(root, "rev-parse", "--is-shallow-repository").strip() != b"false"
        or pre_push.git(root, "rev-parse", "HEAD").strip().decode() != tip
    ):
        raise Refusal("unqualified_local_checkout")
    for revision in (base, tip):
        if pre_push.git(root, "cat-file", "-t", revision).strip() != b"commit":
            raise Refusal("missing_source_commit")
    pre_push.git(root, "merge-base", "--is-ancestor", base, tip)
    items = pre_push.selected_text(root, tip, [base], policy)
    if (
        len(items) > policy["maxBlobs"]
        or sum(len(item["text"].encode("utf-8")) for item in items)
        > policy["maxTotalBytes"]
    ):
        raise Refusal("source_scope_limit")
    # Run even if the range is empty: model and exact review controls must be valid.
    print("Public CI: source range admitted; offline semantic verification required.")
    pre_push.scanner(root, items, policy)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci-base", required=True)
    parser.add_argument("--ci-tip", required=True)
    args = parser.parse_args()
    try:
        policy = json.loads((Path(__file__).resolve().parent / "presidio-policy.json").read_text())
        state = json.loads(pre_push.run([
            "gh", "api", "--hostname", "github.com",
            "repos/" + policy["repository"],
        ]))
        validate_context(policy, state, os.environ)
        verify_range(args.ci_base, args.ci_tip, policy)
        print("Public CI: offline semantic privacy range qualified.")
        return 0
    except Refusal as error:
        category = classify_refusal(error)
        print("Public CI: " + category + "; evidence withheld.", file=sys.stderr)
        return 1
    except Exception:  # noqa: BLE001 -- never expose source, person or subprocess details
        print("Public CI: source identity or semantic privacy range not qualified.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
