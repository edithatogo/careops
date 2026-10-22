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


def check_postpone_intervals(definition: dict, minimum_seconds: int) -> dict:
    """Check literal relative Wait actions; caller must qualify the target profile."""
    if type(minimum_seconds) is not int or minimum_seconds not in (1, 5):
        raise ValueError('Minimum postpone seconds must be 1 or 5.')
    checked = 0
    absolute = 0

    def walk(actions):
        nonlocal checked, absolute
        if not isinstance(actions, dict):
            raise ValueError('An action container must be an object.')
        for action in actions.values():
            if not isinstance(action, dict):
                raise ValueError('An action must be an object.')
            kind = action.get('type')
            if kind == 'Wait':
                inputs = action.get('inputs')
                if not isinstance(inputs, dict):
                    raise ValueError('Wait inputs require separate native qualification.')
                if set(inputs) == {'until'}:
                    absolute += 1
                    continue
                interval = inputs.get('interval')
                if (set(inputs) != {'interval'} or not isinstance(interval, dict)
                        or set(interval) != {'count', 'unit'}):
                    raise ValueError('Relative Wait shape requires separate native qualification.')
                count, unit = interval['count'], interval['unit']
                if (type(count) is not int or count <= 0
                        or unit not in ('Second', 'Minute', 'Hour', 'Day', 'Week', 'Month')):
                    raise ValueError('Relative Wait needs a positive literal integer and known unit; native qualification required.')
                if unit == 'Second' and count < minimum_seconds:
                    raise ValueError('Relative Wait is below the selected minimum postpone interval.')
                checked += 1
            elif kind in ('Foreach', 'Until', 'Scope'):
                walk(action.get('actions', {}))
            elif kind == 'If':
                walk(action.get('actions', {}))
                walk(action.get('else', {}).get('actions', {}))
            elif kind == 'Switch':
                for case in action.get('cases', {}).values():
                    walk(case.get('actions', {}))
                walk(action.get('default', {}).get('actions', {}))

    walk(definition.get('actions', {}))
    return {'minimumSeconds': minimum_seconds, 'relativeWaitCount': checked,
            'absoluteWaitCountExcluded': absolute, 'performanceProfileVerified': False,
            'scope': 'Literal relative Wait minimum only; excludes triggers, absolute waits, provider pacing and runtime.'}


def verify(artifact: Path, member: str, snapshot: Path, minimum_postpone_seconds: int | None = None) -> dict:
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
    timing = (check_postpone_intervals(service['definition'], minimum_postpone_seconds)
              if minimum_postpone_seconds is not None else None)
    return {
        'postponeIntervalCheck': timing,
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
    parser.add_argument('--minimum-postpone-seconds', type=int, choices=(1, 5),
                        help='Opt-in literal Wait check; independently qualify the target performance profile first.')
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise ValueError('Preserve existing evidence; choose a new output revision.')
    result = verify(args.artifact, args.workflow_member, args.snapshot, args.minimum_postpone_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print('Selected workflow export parity passed; no native operation performed.')


if __name__ == '__main__':
    main()
