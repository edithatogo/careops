# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Bind private source candidates to build outputs and retain evidence once."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

REPOSITORY = 'edithatogo/careops'
PRIMARY = ('careops-ppg-portable.zip', 'careops-ppg.spdx.json', 'package.json', 'PPG-submission-assembler.html')
BYTE_EVIDENCE = ('candidate-byte-verification.json', 'native-release-record.json')
SIGNATURES = ('build-attestation.jsonl', 'sbom-attestation.jsonl', 'provenance-verification.json', 'sbom-verification.json')
EVIDENCE_NAME = re.compile(r'attempt-([1-9][0-9]*)-(?:' + '|'.join(re.escape(x) for x in (*BYTE_EVIDENCE, *SIGNATURES)) + r')')

def require(condition, code):
    if not condition:
        raise ValueError(code)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def local_hashes(directory):
    return {name: digest(Path(directory) / name) for name in PRIMARY}

def expected_hashes(env):
    value = json.loads(env['BUILT_HASHES'])
    require(isinstance(value, dict) and set(value) == set(PRIMARY), 'BUILD_HASH_SCOPE')
    require(all(isinstance(x, str) and re.fullmatch('[a-f0-9]{64}', x) for x in value.values()), 'BUILD_HASH_REQUIRED')
    return value

def check_local(directory, env):
    expected = expected_hashes(env)
    require(local_hashes(directory) == expected, 'BUILD_OUTPUT_BYTES_DIFFER')
    return expected

def output(env, key, value):
    with Path(env['GITHUB_OUTPUT']).open('a', encoding='utf-8') as stream:
        stream.write(key + '=' + json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n')

def freeze(directory, env):
    hashes = local_hashes(directory)
    output(env, 'built_hashes', hashes)
    return hashes

def gh(args):
    result = subprocess.run(['gh', *args], capture_output=True, check=False, timeout=120)
    require(result.returncode == 0, 'GH_OPERATION_FAILED_OR_UNCERTAIN')
    return result.stdout

def state(env, tag, run):
    require(env['GITHUB_REPOSITORY'] == REPOSITORY and env['GITHUB_REF'] == 'refs/heads/main', 'MAIN_PRIVATE_SOURCE_REQUIRED')
    require(re.fullmatch('[a-f0-9]{40}', env['GITHUB_SHA']) and re.fullmatch('[1-9][0-9]*', env['GITHUB_RUN_ID']), 'SOURCE_RUN_REQUIRED')
    require(re.fullmatch('[1-9][0-9]*', env['GITHUB_RUN_ATTEMPT']), 'ATTEMPT_REQUIRED')
    prefix = 'careops-ppg-candidate-' + env['GITHUB_SHA'] + '-' + env['GITHUB_RUN_ID'] + '-'
    suffix = tag.removeprefix(prefix)
    require(tag.startswith(prefix) and re.fullmatch('[1-9][0-9]*', suffix) and int(suffix) <= int(env['GITHUB_RUN_ATTEMPT']), 'EXACT_RUN_CANDIDATE_REQUIRED')
    require(json.loads(run(['api', 'repos/' + REPOSITORY, '--jq', '.private'])) is True, 'PRIVATE_DESTINATION_REQUIRED')
    metadata = json.loads(run(['release', 'view', tag, '--repo', REPOSITORY, '--json', 'apiUrl,isDraft,targetCommitish,assets']))
    require(metadata['isDraft'] is True and metadata['targetCommitish'] == env['GITHUB_SHA'], 'CANDIDATE_SOURCE_DIFFERS')
    require(re.fullmatch(r'https://api\.github\.com/repos/edithatogo/careops/releases/[1-9][0-9]*', metadata['apiUrl']), 'CANDIDATE_API_REQUIRED')
    assets = metadata['assets']
    require(isinstance(assets, list) and 4 <= len(assets) <= 1000, 'ASSET_SCOPE')
    require(len({a['name'] for a in assets}) == len(assets) and len({a['id'] for a in assets}) == len(assets), 'DUPLICATE_ASSET_IDENTITY')
    for asset in assets:
        match = EVIDENCE_NAME.fullmatch(asset['name'])
        require(asset['id'] and (asset['name'] in PRIMARY or (match and int(match.group(1)) <= int(env['GITHUB_RUN_ATTEMPT']))), 'UNKNOWN_ASSET_IDENTITY')
    return metadata

def primary_records(metadata, hashes):
    records = {}
    for name in PRIMARY:
        matches = [a for a in metadata['assets'] if a['name'] == name]
        require(len(matches) == 1 and matches[0]['digest'] == 'sha256:' + hashes[name], 'PRIMARY_ASSET_DIFFERS_FROM_BUILD')
        records[name] = {'assetId': matches[0]['id'], 'sha256': hashes[name]}
    return records

def bound_records(metadata, env):
    hashes = expected_hashes(env)
    trusted = json.loads(env['BUILT_ASSETS'])
    require(isinstance(trusted, dict) and set(trusted) == set(PRIMARY), 'BUILD_ASSET_SCOPE')
    actual = primary_records(metadata, hashes)
    require(actual == trusted, 'PUBLISHED_ASSET_IDENTITY_CHANGED')
    return actual

def capture(directory, env, tag, run=gh):
    hashes = check_local(directory, env)
    records = primary_records(state(env, tag, run), hashes)
    output(env, 'built_assets', records)
    return records

def write_exact(path, value):
    content = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()
    if path.exists():
        require(path.read_bytes() == content, 'PRESERVE_CHANGED_LOCAL_EVIDENCE')
    else:
        with path.open('xb') as stream:
            stream.write(content)

def verify(directory, env, tag, run=gh):
    folder = Path(directory)
    hashes = check_local(folder, env)
    metadata = state(env, tag, run)
    records = bound_records(metadata, env)
    manifest = json.loads((folder / 'package.json').read_text())
    require(manifest['sourceCommit'] == env['GITHUB_SHA'] and manifest['nativeWrites'] is False, 'MANIFEST_SOURCE_DIFFERS')
    require(manifest['archiveSha256'] == hashes[PRIMARY[0]] and manifest['assemblerSha256'] == hashes[PRIMARY[3]], 'MANIFEST_BYTES_DIFFER')
    document = json.loads((folder / PRIMARY[1]).read_text())
    require(document['packages'][0]['sourceInfo'] == 'Source commit: ' + env['GITHUB_SHA'] and document['packages'][0]['licenseDeclared'] == 'Apache-2.0', 'INVENTORY_SOURCE_DIFFERS')
    require(document['packages'][0]['checksums'][0]['checksumValue'] == hashes[PRIMARY[0]], 'INVENTORY_ARCHIVE_DIFFERS')
    with zipfile.ZipFile(folder / PRIMARY[0]) as archive:
        entries = [x for x in archive.infolist() if not x.is_dir()]
        require(len({x.filename for x in entries}) == len(entries), 'DUPLICATE_ARCHIVE_IDENTITY')
        actual = {x.filename: hashlib.sha256(archive.read(x)).hexdigest() for x in entries}
        require(archive.read(PRIMARY[3]) == (folder / PRIMARY[3]).read_bytes(), 'ASSEMBLER_SIDECAR_DIFFERS')
    declared = {x['fileName'].removeprefix('./'): next(c['checksumValue'] for c in x['checksums'] if c['algorithm'] == 'SHA256') for x in document['files']}
    require(actual and len(declared) == len(document['files']) and actual == declared, 'INVENTORY_FILE_BYTES_DIFFER')
    # Freeze only primary identities. Download counters and partially retained
    # auxiliary evidence must not change the bytes of a recovery receipt.
    native = {k: metadata[k] for k in ('apiUrl', 'isDraft', 'targetCommitish')}
    native['assets'] = records
    receipt = {'schemaVersion': 1, 'phase': 'source-candidate-byte-verification', 'repository': REPOSITORY,
        'sourceCommit': env['GITHUB_SHA'], 'sourceRef': env['GITHUB_REF'], 'runId': env['GITHUB_RUN_ID'],
        'candidateTag': tag, 'assets': records, 'trustedBuildHashesVerified': True,
        'allArchiveFileHashesVerified': True, 'nativeAttestationExecuted': False,
        'signedReleaseQualified': False, 'nativeDeploymentQualified': False}
    write_exact(folder / 'native-release-record.json', native)
    write_exact(folder / 'candidate-byte-verification.json', receipt)
    return receipt

def retain(directory, env, tag, kind='bytes', run=gh):
    require(kind in ('bytes', 'signatures'), 'EVIDENCE_KIND_REQUIRED')
    metadata = state(env, tag, run)
    bound_records(metadata, env)
    folder = Path(directory)
    names = BYTE_EVIDENCE if kind == 'bytes' else SIGNATURES
    paths = [folder / name for name in names if (folder / name).is_file()]
    require(kind != 'bytes' or len(paths) == 2, 'COMPLETE_BYTE_EVIDENCE_REQUIRED')
    staging = folder / 'retention'
    staging.mkdir(exist_ok=True)
    expected = {}
    for path in paths:
        name = 'attempt-' + env['GITHUB_RUN_ATTEMPT'] + '-' + path.name
        target = staging / name
        content = path.read_bytes()
        if target.exists():
            require(target.read_bytes() == content, 'PRESERVE_CHANGED_LOCAL_EVIDENCE')
        else:
            with target.open('xb') as stream:
                stream.write(content)
        expected[name] = (target, hashlib.sha256(content).hexdigest())
    before = {a['name']: a for a in metadata['assets']}
    # Check the entire pair before the first write, including partial outcomes.
    for name, (_, wanted) in expected.items():
        require(name not in before or before[name]['digest'] == 'sha256:' + wanted, 'PRESERVE_CHANGED_EVIDENCE_ASSET')
    created = preserved = 0
    for name, (path, wanted) in expected.items():
        current = state(env, tag, run)
        bound_records(current, env)
        found = next((a for a in current['assets'] if a['name'] == name), None)
        if found:
            require(found['digest'] == 'sha256:' + wanted, 'PRESERVE_CHANGED_EVIDENCE_ASSET')
            preserved += 1
        else:
            run(['release', 'upload', tag, str(path.resolve()), '--repo', REPOSITORY])
            created += 1  # One invocation only; an uncertain result is not retried.
        after = state(env, tag, run)
        bound_records(after, env)
        actual = next((a for a in after['assets'] if a['name'] == name), None)
        require(actual and actual['digest'] == 'sha256:' + wanted, 'EVIDENCE_READBACK_DIFFERS')
    final = state(env, tag, run)
    bound_records(final, env)
    final_by_name = {a['name']: a for a in final['assets']}
    for name in expected.keys() & before.keys():
        require(final_by_name[name]['id'] == before[name]['id'] and final_by_name[name]['digest'] == before[name]['digest'], 'PRESERVED_EVIDENCE_CHANGED')
    return {'created': created, 'preserved': preserved}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('freeze', 'check', 'capture', 'verify', 'retain'))
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--tag', default=os.environ.get('CANDIDATE_TAG', ''))
    parser.add_argument('--kind', choices=('bytes', 'signatures'), default='bytes')
    args = parser.parse_args()
    try:
        if args.mode == 'freeze': freeze(args.directory, os.environ)
        elif args.mode == 'check': check_local(args.directory, os.environ)
        elif args.mode == 'capture': capture(args.directory, os.environ, args.tag)
        elif args.mode == 'verify': verify(args.directory, os.environ, args.tag)
        else: retain(args.directory, os.environ, args.tag, args.kind)
        print('Candidate evidence operation verified; no signed-release claim.')
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError, StopIteration, zipfile.BadZipFile):
        raise SystemExit('Candidate evidence operation refused; preserve current state for reconciliation.') from None

if __name__ == '__main__':
    main()
