"""Read committed ALM source only; never authenticate, export or mutate a tenant."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(['git', '--no-replace-objects', '-C', str(root), *args])


def inspect_solution(data: bytes) -> dict:
    xml = ET.fromstring(data)
    keys = []
    for component in xml.findall('.//RootComponent'):
        identity = component.get('schemaName') or component.get('id')
        # GUID spelling does not distinguish native components. Do not infer a
        # schema-name/ID mapping or merge different component types.
        if not component.get('schemaName') and identity:
            try:
                identity = str(uuid.UUID(identity))
            except ValueError:
                pass
        keys.append((component.get('type'), identity))
    version = xml.findtext('.//SolutionManifest/Version')
    return {'uniqueName': xml.findtext('.//UniqueName'),
            'version': version,
            'versionFormatValid': bool(re.fullmatch(r'[0-9]+(?:\.[0-9]+){3}', version or '')),
            'publisherUniqueName': xml.findtext('.//SolutionManifest/Publisher/UniqueName'),
            'publisherPrefix': xml.findtext('.//SolutionManifest/Publisher/CustomizationPrefix'),
            'managed': xml.findtext('.//Managed'),
            'rootComponentCount': len(keys),
            'duplicateRootKeys': len(keys) - len(set(keys)),
            'sha256': hashlib.sha256(data).hexdigest()}


def audit(root: Path, revision: str = 'HEAD') -> dict:
    # Resolve once: a concurrent owner commit cannot mix source revisions.
    commit = git(root, 'rev-parse', '--verify', revision + '^{commit}').decode().strip()
    entries = git(root, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0')
    files = {}
    for entry in entries:
        if not entry:
            continue
        meta, raw = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind == 'blob' and mode in ('100644', '100755'):
            files[raw.decode()] = oid
    solutions = []
    for name, oid in files.items():
        if name.lower().endswith('/solution.xml'):
            try:
                record = inspect_solution(git(root, 'cat-file', 'blob', oid))
            except ET.ParseError:
                record = {'error': 'invalid-solution-xml'}
            solutions.append({'path': name, **record})
    names = list(files)
    return {'sourceCommit': commit, 'scope': 'committed-source-only',
            'trackedFiles': len(names), 'solutions': solutions,
            'workflowFiles': sum(n.startswith('.github/workflows/') and n.endswith(('.yml', '.yaml')) for n in names),
            'connectionReferenceFiles': sum('connectionreferences/' in n.lower() for n in names),
            'environmentDefinitionFiles': sum('environmentvariabledefinitions/' in n.lower() for n in names),
            'deploymentSettingsFiles': sum('deployment' in n.lower() and 'setting' in n.lower() and n.endswith('.json') for n in names),
            'nativeCoverage': 'not-verified', 'dependencyClosure': 'not-verified',
            'externalArtifactCoverage': 'requires-owner-manifest-reconciliation'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--revision', default='HEAD')
    args = parser.parse_args()
    print(json.dumps(audit(args.repository, args.revision), indent=2))
