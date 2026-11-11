"""Read-only GitHub Actions evidence acquisition for exact CareOps commit heads.

No GitHub mutations, no raw logs/annotations written. The authenticated `gh api`
client supplies evidence; protection readback is distinct from execution state.
An unavailable permission or unknown Actions job fails closed.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from typing import Any, Callable

from frontier_ci_evidence import classify_snapshot

REPOSITORY = "edithatogo/careops"
SHA = re.compile(r"^[0-9a-f]{40}$")
BILLING = re.compile(r"recent account payments have failed|spending limit needs to be increased|billing.{0,60}(?:limit|payment)", re.I)
MAX_PAGES = 12
API = Callable[[str], Any]


class CollectionError(ValueError):
    pass


def gh_api(path: str) -> Any:
    """Fixed read-only GET requests; never interpolate arguments through a shell."""
    allowed = (
        rf"/repos/{REPOSITORY}/branches/main/protection/required_status_checks",
        rf"/repos/{REPOSITORY}/commits/[a-f0-9]{{40}}/check-runs\?per_page=100&page=(?:[1-9]|1[0-2])",
        rf"/repos/{REPOSITORY}/actions/jobs/[1-9][0-9]*",
        rf"/repos/{REPOSITORY}/actions/runs/[1-9][0-9]*",
        rf"/repos/{REPOSITORY}/check-runs/[1-9][0-9]*/annotations\?per_page=100",
    )
    if not isinstance(path, str) or not any(re.fullmatch(rule, path) for rule in allowed):
        raise CollectionError("unapproved-api-path")
    try:
        result = subprocess.run(
            ["gh", "api", "--method", "GET", path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CollectionError("github-api-unavailable") from exc
    if result.returncode or len(result.stdout) > 4_000_000:
        raise CollectionError("github-api-refused")
    try:
        return json.loads(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise CollectionError("github-api-invalid-json") from exc


def _check_run_pages(sha: str, api: API) -> list[dict]:
    records: list[dict] = []
    expected_count: int | None = None
    for page in range(1, MAX_PAGES + 1):
        data = api(f"/repos/{REPOSITORY}/commits/{sha}/check-runs?per_page=100&page={page}")
        if not isinstance(data, dict) or not isinstance(data.get("check_runs"), list):
            raise CollectionError("invalid-check-page")
        count = data.get("total_count")
        if type(count) is not int or count < 0 or count > MAX_PAGES * 100:
            raise CollectionError("invalid-check-count")
        if expected_count is None:
            expected_count = count
        if count != expected_count:
            raise CollectionError("changing-check-page-count")
        entries = data["check_runs"]
        if any(not isinstance(x, dict) for x in entries):
            raise CollectionError("invalid-check-record")
        records.extend(entries)
        if len(records) >= count:
            break
        if not entries:
            raise CollectionError("incomplete-check-pages")
    if len(records) != expected_count:
        raise CollectionError("incomplete-check-pages")
    ids = [x.get("id") for x in records]
    if any(type(i) is not int or i <= 0 for i in ids) or len(ids) != len(set(ids)):
        raise CollectionError("duplicate-or-invalid-check-identity")
    return records


def collect(sha: str, api: API = gh_api, *, branch: str = "main") -> dict:
    """Collect sanitised evidence and classify it; no merge rights are asserted.

    Branch protection may be unavailable to this token. It is not replaced by
    a guessed set of required jobs. Always retain protection_verified=False
    unless the actual exact branch protection endpoint responds.
    """
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise CollectionError("invalid-source-sha")
    if branch != "main":
        raise CollectionError("unsupported-protection-branch")
    try:
        protection = api(f"/repos/{REPOSITORY}/branches/{branch}/protection/required_status_checks")
        contexts = protection.get("contexts", [])
        checks_data = protection.get("checks", [])
        if not isinstance(contexts, list) or not isinstance(checks_data, list):
            raise CollectionError("invalid-branch-protection")
        required = sorted(set(contexts + [v["context"] for v in checks_data]))
        if not required or any(not isinstance(x, str) or not x for x in required):
            raise CollectionError("unqualified-required-checks")
        protection_verified = True
    except (CollectionError, KeyError, TypeError, ValueError):
        required = []
        protection_verified = False
    checks = _check_run_pages(sha, api)
    # Without actual protection readback, retain a bounded diagnostic view, but
    # never call this a qualified exact-head set.
    names = required or sorted(set(c.get("name") for c in checks if isinstance(c.get("name"), str)))
    if not names:
        return {"source_sha": sha, "state": "unverified", "reason": "no-checks",
                "branch_protection_verified": protection_verified, "protected_merge_qualified": False}
    snapshots = []
    for check in checks:
        name = check.get("name")
        if name not in names:
            continue
        if check.get("head_sha") != sha:
            raise CollectionError("stale-check-source")
        steps = []
        annotations = []
        app = check.get("app") or {}
        if app.get("slug") == "github-actions":
            check_id = check["id"]
            try:
                job = api(f"/repos/{REPOSITORY}/actions/jobs/{check_id}")
                run_id = job.get("run_id")
                if type(run_id) is not int or job.get("id") != check_id:
                    raise CollectionError("job-identity-unqualified")
                run = api(f"/repos/{REPOSITORY}/actions/runs/{run_id}")
                if run.get("head_sha") != sha:
                    raise CollectionError("job-run-stale-source")
                raw = job.get("steps", [])
                if not isinstance(raw, list):
                    raise CollectionError("job-steps-invalid")
                steps = [{"status": x.get("status"), "conclusion": x.get("conclusion")}
                         for x in raw if isinstance(x, dict)]
            except (CollectionError, KeyError, TypeError, ValueError):
                steps = []
        # Only a billing indicator is retained; no raw annotation text escapes.
        try:
            raw_annotations = api(f"/repos/{REPOSITORY}/check-runs/{check['id']}/annotations?per_page=100")
            if isinstance(raw_annotations, list) and any(
                    BILLING.search(str(a.get("message", "")))
                    for a in raw_annotations if isinstance(a, dict)):
                annotations = [{"message": "billing spending limit"}]
        except (CollectionError, TypeError, ValueError):
            pass
        snapshots.append({"name": name, "head_sha": sha,
                          "status": check.get("status"), "conclusion": check.get("conclusion"),
                          "steps": steps, "annotations": annotations})
    result = classify_snapshot({"schema_version": 1, "head_sha": sha,
                                "required": names, "checks": snapshots})
    if not protection_verified and result["state"] == "passed-executed":
        result["state"] = "unverified-protection"
    result["branch_protection_verified"] = protection_verified
    result["protected_merge_qualified"] = False
    result["collector"] = "read-only-gh-api"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    try:
        value = collect(args.source_sha)
    except (CollectionError, ValueError, TypeError):
        parser.exit(2, "CI collector refused: source or API qualification unavailable\n")
    print(json.dumps(value, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
