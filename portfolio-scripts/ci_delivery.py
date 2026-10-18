"""Shared source-only CI primitives: exact resolution, locks and honest outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

PIN = re.compile(r'^([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9_.+!-]*)$')
SHA = re.compile(r'^[a-f0-9]{40}$')
BILLING = re.compile(r'recent account payments have failed|spending limit needs to be increased|billing.*(?:limit|payment)', re.I)


def exact_requirements(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = PIN.fullmatch(line)
        if not match:
            raise ValueError('CI requirements must contain exact registry pins only.')
        name, version = match.groups()
        key = re.sub(r'[-_.]+', '-', name).lower()
        if key in result:
            raise ValueError('Duplicate CI dependency.')
        result[key] = version
    if not result:
        raise ValueError('Empty CI requirements.')
    return result


def peel_commit(obj: dict, get_tag) -> str:
    """Resolve annotated tags to commits; comparing tag-object IDs is incorrect."""
    seen = set()
    for _ in range(8):
        kind, sha = obj.get('type'), obj.get('sha', '')
        if not isinstance(sha, str) or not SHA.fullmatch(sha) or sha in seen:
            raise ValueError('Invalid or cyclic upstream reference.')
        seen.add(sha)
        if kind == 'commit':
            return sha
        if kind != 'tag':
            raise ValueError('Upstream reference does not identify a commit.')
        obj = get_tag(sha)['object']
    raise ValueError('Too many annotated tag layers.')


def classify_run(run: dict, jobs: list[dict], annotations: list[dict]) -> dict:
    """A job refused before execution is blocked, never a tested failure/pass."""
    billing = any(BILLING.search(str(a.get('message', ''))) for a in annotations)
    failures = [j.get('name', 'unnamed') for j in jobs if j.get('conclusion') == 'failure' and any(s.get('status') == 'completed' and s.get('conclusion') not in ['skipped', None] for s in j.get('steps', []))]
    if run.get('status') != 'completed':
        state = 'pending'
    elif failures:
        state = 'executed-failure'
    elif billing and run.get('conclusion') != 'success':
        state = 'billing-blocked'
    elif run.get('conclusion') == 'success' and jobs and any(j.get('conclusion') == 'success' for j in jobs) and all(j.get('conclusion') in ['success', 'skipped'] for j in jobs):
        state = 'passed'
    elif run.get('conclusion') in ['cancelled', 'skipped', 'timed_out']:
        state = run['conclusion']
    else:
        state = 'unverified-failure' if run.get('conclusion') == 'failure' else 'unverified'
    return {'state': state, 'billingAnnotationPresent': billing, 'executedFailureJobs': failures, 'runId': run.get('id'), 'headSha': run.get('head_sha'), 'operationalAcceptance': False}


def regenerate(root: Path, output: Path, *, preview: bool = False) -> dict:
    if not output.resolve().is_relative_to(root.resolve()):
        raise ValueError('Generated lock must stay inside the selected source workspace.')
    requirements = root / 'requirements-ci.txt'
    pins = exact_requirements(requirements)
    source = requirements
    if preview:
        source = output.with_suffix('.in')
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('\n'.join(pins) + '\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['uv', 'pip', 'compile', str(source.relative_to(root)), '--no-config', '--generate-hashes', '--python-version', '3.13', '--output-file', str(output.relative_to(root)), '--quiet']
    if preview:
        cmd += ['--upgrade', '--prerelease', 'allow']
    subprocess.run(cmd, cwd=root, check=True)
    # The candidate receipt contains exact package versions and a lock digest,
    # never credential stores, native data or arbitrary registry URLs.
    resolved = {}
    for line in output.read_text().splitlines():
        match = re.match(r'^([A-Za-z0-9_.-]+)==([^ \\]+)', line)
        if match:
            resolved[match[1]] = match[2]
    if not resolved or '--hash=sha256:' not in output.read_text():
        raise ValueError('Generated lock is incomplete.')
    return {'channel': 'preview-candidate' if preview else 'declared-exact-pins', 'dependencies': resolved, 'lockSha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'promoted': False, 'nativeWrites': False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    lock = sub.add_parser('lock')
    lock.add_argument('--root', type=Path, default=Path('.'))
    lock.add_argument('--output', type=Path, required=True)
    lock.add_argument('--receipt', type=Path, required=True)
    lock.add_argument('--preview', action='store_true')
    outcome = sub.add_parser('classify')
    outcome.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'lock':
        result = regenerate(args.root.resolve(), args.output.resolve(), preview=args.preview)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    else:
        data = json.loads(args.input.read_text())
        result = classify_run(data['run'], data.get('jobs', []), data.get('annotations', []))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
