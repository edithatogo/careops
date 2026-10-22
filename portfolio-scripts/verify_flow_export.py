"""Compare one exported cloud flow with a retained service snapshot, entirely offline."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath

MAX_BYTES = 64 * 1024 * 1024
MAX_MEMBERS = 10_000


def strict_json(raw: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON property.')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('Non-JSON numeric constant.')
    value = json.loads(raw, object_pairs_hook=unique, parse_constant=invalid_constant)
    if not isinstance(value, dict):
        raise ValueError('A JSON object is required.')
    return value


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def verify(artifact: Path, member: str, snapshot: Path) -> dict:
    for path in (artifact, snapshot):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError('Bounded regular input files are required.')
    package_bytes, snapshot_bytes = artifact.read_bytes(), snapshot.read_bytes()
    service = strict_json(snapshot_bytes)['properties']
    if not isinstance(service.get('definition'), dict) or not service['definition']:
        raise ValueError('A retained service definition is required.')
    with zipfile.ZipFile(io.BytesIO(package_bytes)) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_MEMBERS or sum(x.file_size for x in entries) > MAX_BYTES:
            raise ValueError('Archive exceeds bounded limits.')
        names = set()
        for entry in entries:
            name, path = entry.filename, PurePosixPath(entry.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name
                    or str(path) != name.rstrip('/') or any(ord(c) < 32 for c in name)
                    or name.rstrip('/').casefold() in names or entry.flag_bits & 1):
                raise ValueError('Unsafe, duplicate or encrypted archive identity.')
            names.add(name.rstrip('/').casefold())
        entry = archive.getinfo(member)
        if entry.is_dir() or not member.startswith('Workflows/') or not member.endswith('.json'):
            raise ValueError('Select an exact exported workflow JSON member.')
        with archive.open(entry) as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) != entry.file_size or len(raw) > MAX_BYTES:
            raise ValueError('Workflow content exceeds declared limits.')
    exported = strict_json(raw)
    if set(exported) != {'properties', 'schemaVersion'} or exported['schemaVersion'] != '1.0.0.0':
        raise ValueError('Unsupported workflow envelope.')
    props = exported['properties']
    if not isinstance(props, dict) or set(props) - {'definition', 'connectionReferences', 'templateName'}:
        raise ValueError('Uncompared exported workflow properties.')
    if props.get('templateName') is not None:
        raise ValueError('A non-null template name requires separate qualification.')
    if canonical(props.get('definition')) != canonical(service['definition']):
        raise ValueError('Exported definition differs from the service snapshot.')
    refs, native = props.get('connectionReferences'), service.get('connectionReferences')
    if not isinstance(refs, dict) or not isinstance(native, dict) or set(refs) != set(native):
        raise ValueError('Connection reference coverage differs.')
    for key, ref in refs.items():
        if (not isinstance(ref, dict) or set(ref) != {'runtimeSource', 'connection', 'api'}
                or not isinstance(ref['connection'], dict) or not isinstance(ref['api'], dict)
                or set(ref['connection']) != {'connectionReferenceLogicalName'}
                or set(ref['api']) != {'name'}):
            raise ValueError('Unsupported package reference representation.')
        old = native[key]
        if (not isinstance(old, dict) or not isinstance(ref['runtimeSource'], str) or not isinstance(old.get('source'), str)
                or ref['runtimeSource'].casefold() not in {'invoker', 'embedded'}
                or ref['runtimeSource'].casefold() != old['source'].casefold()
                or not ref['connection']['connectionReferenceLogicalName']
                or ref['connection']['connectionReferenceLogicalName'] != old.get('connectionReferenceLogicalName')
                or not ref['api']['name']
                or old.get('id') != '/providers/Microsoft.PowerApps/apis/' + ref['api']['name']):
            raise ValueError('Connection identity, API or invocation source differs.')
    return {
        'schemaVersion': 1, 'qualified': True,
        'scope': 'One exported workflow compared with a supplied retained service snapshot; no network calls.',
        'artifactSha256': hashlib.sha256(package_bytes).hexdigest(),
        'snapshotSha256': hashlib.sha256(snapshot_bytes).hexdigest(),
        'workflowSha256': hashlib.sha256(raw).hexdigest(),
        'definitionExact': True, 'connectionReferenceCount': len(refs),
        'referenceMapping': 'logical name, full connector API id and case-insensitive invocation source',
        'nativeSnapshotAuthenticityVerified': False, 'workflowIdentityVerified': False,
        'wholeSolutionCoverageVerified': False,
        'runtimeOrImportQualified': False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--workflow-member', required=True)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise ValueError('Preserve existing evidence; choose a new output revision.')
    result = verify(args.artifact, args.workflow_member, args.snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print('Selected workflow export parity passed; no native operation performed.')


if __name__ == '__main__':
    main()
