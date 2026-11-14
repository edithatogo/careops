"""Validate the reviewed public-source boundary without reading private stores."""
from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> list[str]:
    manifest = json.loads((root / 'PUBLIC_SOURCE_FILES.json').read_text())
    policy_path = root / '.careops-security/policy.json'
    approvals = json.loads(policy_path.read_text()).get('reviewedArtifacts', {}) if policy_path.exists() else {}
    expected = manifest['files']
    problems = []
    if len(expected) != len(set(expected)):
        problems.append('Duplicate inventory paths')
    for name in expected:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name:
            problems.append('Unsafe inventory path')
    git = shutil.which('git')
    if git is None:
        raise FileNotFoundError('Git executable is unavailable')
    listed = subprocess.check_output([str(Path(git).resolve(strict=True)), '-C', str(root), 'ls-files', '--stage', '-z'])
    actual = {}
    for entry in listed.split(b'\0'):
        if entry:
            metadata, raw = entry.split(b'\t', 1)
            mode, revision, stage = metadata.decode().split()
            name = raw.decode()
            if stage != '0' or name in actual:
                problems.append('Unmerged or duplicate index entry')
            actual[name] = (mode, revision)
    if set(actual) != set(expected):
        problems.append('Tracked files differ from reviewed inventory: ' + ', '.join(sorted(set(actual) ^ set(expected))))
    forbidden = re.compile(r'(?i)(?:[A-Z0-9._%+-]+@health\.[A-Z.]+\.gov\.au|\b[a-z0-9.-]+\.ghe\.com\b|(?-i:/(?:Users|Volumes)/[^/\s]+/))')
    for name, (mode, revision) in actual.items():
        if mode == '160000':
            if manifest['gitlinks'].get(name) != revision:
                problems.append('Unreviewed submodule revision: ' + name)
            continue
        path = root / name
        if mode not in ('100644', '100755') or path.is_symlink():
            problems.append('Unsupported public-source file type: ' + name)
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            approval = approvals.get(name, {})
            if (not path.is_file() or not str(approval.get('reason', '')).strip()
                    or approval.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest()):
                problems.append('Missing or binary public-source file: ' + name)
            continue
        if '\0' in text or forbidden.search(text):
            problems.append('Private reference or binary content: ' + name)
    return problems


if __name__ == '__main__':
    errors = validate()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Reviewed public-source inventory and privacy boundary passed.')
