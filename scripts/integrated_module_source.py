"""Verify maintained integrated module source without legacy checkouts."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

MODULES = {'careops-process': 'modules/careops-process', 'careops-approve': 'careops-approve', **{f'careops-{name}': f'modules/careops-{name}' for name in ('finance', 'costing')}}


def validate_integrated_modules(root: Path) -> list[str]:
    errors: list[str] = []
    qualification = json.loads((root / 'portfolio/public-runtime-compatibility.json').read_text())
    topology = json.loads((root / 'portfolio/repos.json').read_text())
    publication = json.loads((root / 'PUBLIC_SOURCE_FILES.json').read_text())
    for name, prefix in MODULES.items():
        module = root / prefix
        provenance = json.loads((module / 'SOURCE_PROVENANCE.json').read_text())
        selected = [item for item in topology['components'] if item['name'] == name]
        sha = provenance['sourceCommit']
        if (re.fullmatch('[0-9a-f]{40}', sha) is None or len(selected) != 1
                or selected[0].get('materialization') != 'integrated-source'
                or selected[0].get('sourceBaseline') != sha or selected[0].get('path') != prefix
                or (name in ('careops-process', 'careops-approve') and (qualification['modules'].get(name) != sha
                or qualification.get('modulePaths', {}).get(name) != prefix))
                or prefix in publication['gitlinks']):
            errors.append('Integrated source selection mismatch: ' + name)
        entries = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--stage', '-z', '--', prefix])
        actual = set()
        for entry in entries.split(b'\0'):
            if not entry:
                continue
            meta, path = entry.decode().split('\t', 1)
            mode, _, stage = meta.split()
            if mode not in ('100644', '100755') or stage != '0':
                errors.append('Unsupported integrated entry: ' + path)
            actual.add(path.removeprefix(prefix + '/'))
        declared = provenance['maintainedFiles']
        if actual != set(declared) | {'SOURCE_PROVENANCE.json'}:
            errors.append('Integrated source inventory mismatch: ' + name)
        for relative, record in declared.items():
            digest = record["sha256"] if isinstance(record, dict) else record
            safe = PurePosixPath(relative)
            path = module / relative
            if (safe.is_absolute() or '..' in safe.parts or '\\' in relative
                    or path.is_symlink() or not path.is_file()):
                errors.append('Unsafe or missing integrated file: ' + relative)
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                errors.append('Integrated source digest mismatch: ' + prefix + '/' + relative)
        for path in provenance['sourceFiles']:
            if path not in declared:
                errors.append('Imported text source was lost: ' + prefix + '/' + path)
    return errors
