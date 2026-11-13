"""Print only safe location/rule metadata from a Gitleaks JSON report.

Never log matched values, source snippets, descriptions, author details, or report
contents. Only run after the Gitleaks full-history scan; do not change its scope,
rules, ignore file, exit handling, or native gate.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

SAFE_PATH = re.compile(r"^[A-Za-z0-9_./+@ -]{1,240}$")
SAFE_RULE = re.compile(r"^[a-zA-Z0-9_-]{1,100}$")
COMMIT = re.compile(r"^[a-fA-F0-9]{40}$")


def summarise(report: object, limit: int = 60) -> list[str]:
    if not isinstance(report, list):
        return ["Gitleaks diagnostics unavailable: report is not a JSON findings array."]
    valid: list[tuple[str, str, str, int]] = []
    for entry in report:
        if not isinstance(entry, dict):
            return ["Gitleaks diagnostics unavailable: malformed finding."]
        path = entry.get("File")
        rule = entry.get("RuleID")
        commit = entry.get("Commit")
        line = entry.get("StartLine")
        if not isinstance(path, str) or not SAFE_PATH.fullmatch(path):
            return ["Gitleaks diagnostics unavailable: unsafe path metadata."]
        if not isinstance(rule, str) or not SAFE_RULE.fullmatch(rule):
            return ["Gitleaks diagnostics unavailable: unsafe rule metadata."]
        if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
            return ["Gitleaks diagnostics unavailable: invalid commit metadata."]
        if type(line) is not int or line < 1:
            return ["Gitleaks diagnostics unavailable: invalid line metadata."]
        valid.append((rule, path, commit, line))
    result = [f"Gitleaks full-history findings: {len(valid)} (metadata only, no matched content)."]
    by_rule = Counter(item[0] for item in valid)
    result.append("Rule counts: " + ", ".join(f"{rule}={count}" for rule, count in sorted(by_rule.items())))
    for rule, path, commit, line in valid[:limit]:
        result.append(f"rule={rule} path={path} commit={commit} line={line}")
    if len(valid) > limit:
        result.append(f"Additional findings omitted: {len(valid) - limit}; inspect report privately.")
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: gitleaks_diagnostics.py /private/report.json", file=sys.stderr)
        return 2
    try:
        report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        print("Gitleaks diagnostics unavailable: no readable valid JSON report.")
        return 1
    for line in summarise(report):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
