"""Classify offline GitHub CI evidence without promoting local results to protected merges.

Input must be gathered by a separate authenticated read-only collector; this module
never calls GitHub, runs jobs or handles tokens. It deliberately omits annotations,
step output and arbitrary messages from returned receipts.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_SHA = re.compile(r"[a-f0-9]{40}\Z")
_BILLING = re.compile(r"(?:recent account payments have failed|spending limit needs to be increased|billing.{0,60}(?:limit|payment))", re.I)
_MAX_CHECKS = 1000


class EvidenceError(ValueError):
    """Invalid or unsupported evidence input; never embeds source contents."""


def _valid_check(c: dict) -> bool:
    return (isinstance(c.get('name'), str) and bool(c['name']) and
            isinstance(c.get('head_sha'), str) and bool(_SHA.fullmatch(c['head_sha'])) and
            isinstance(c.get('steps'), list) and all(isinstance(s, dict) for s in c['steps']) and
            isinstance(c.get('annotations', []), list) and
            all(isinstance(a, dict) for a in c.get('annotations', [])))


def classify_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Report only what executed on one exact SHA; never approve a protected merge.

    Missing, duplicate, stale or ambiguous contexts are unverified. Billing
    annotation text is inspected locally then discarded. Source release, branch
    protection, review approvals and native operations require separate evidence.
    """
    if not isinstance(snapshot, dict) or snapshot.get('schema_version') != 1:
        raise EvidenceError('invalid-evidence-schema')
    sha = snapshot.get('head_sha')
    required = snapshot.get('required')
    checks = snapshot.get('checks')
    if (not isinstance(sha, str) or not _SHA.fullmatch(sha) or
            not isinstance(required, list) or not required or
            not all(isinstance(s, str) and 0 < len(s) <= 128 for s in required) or
            len(set(required)) != len(required) or
            not isinstance(checks, list) or len(checks) > _MAX_CHECKS or
            not all(isinstance(c, dict) and _valid_check(c) for c in checks)):
        raise EvidenceError('invalid-evidence-input')

    by_name: dict[str, list[dict]] = {name: [] for name in required}
    for c in checks:
        if c['name'] in by_name:
            by_name[c['name']].append(c)
    issues: list[dict[str, str]] = []
    any_execution_failure = False
    any_billing_block = False
    for name in sorted(required):
        rows = by_name[name]
        if len(rows) != 1:
            issues.append({'check': name, 'reason': 'missing-or-duplicate'})
            continue
        row = rows[0]
        if row['head_sha'] != sha:
            issues.append({'check': name, 'reason': 'stale-source'})
            continue
        steps = row['steps']
        executed = [s for s in steps if s.get('status') == 'completed'
                    and s.get('conclusion') not in (None, 'skipped')]
        billing = any(_BILLING.search(str(a.get('message', '')))
                      for a in row.get('annotations', []))
        if row.get('status') != 'completed':
            issues.append({'check': name, 'reason': 'not-completed'})
        elif row.get('conclusion') == 'success' and executed and all(
                s.get('conclusion') == 'success' for s in steps):
            continue
        elif any(s.get('conclusion') == 'failure' for s in executed):
            any_execution_failure = True
            issues.append({'check': name, 'reason': 'executed-failure'})
        elif billing and not executed:
            any_billing_block = True
            issues.append({'check': name, 'reason': 'billing-blocked'})
        elif row.get('conclusion') == 'success' and not executed:
            issues.append({'check': name, 'reason': 'no-executed-steps'})
        else:
            issues.append({'check': name, 'reason': 'unverified-result'})
    status = ('executed-failure' if any_execution_failure else
              'billing-blocked' if any_billing_block else
              'unverified' if issues else 'passed-executed')
    return {'schema_version': 1, 'source_sha': sha, 'state': status,
            'required_count': len(required), 'unqualified': issues,
            'protected_merge_qualified': False, 'native_deployment_qualified': False,
            'input_provenance_verified': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.input.read_text(encoding='utf-8'))
        result = classify_snapshot(snapshot)
    except (OSError, ValueError, TypeError, EvidenceError):
        parser.exit(2, 'Evidence classification refused: invalid or inaccessible input\n')
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
