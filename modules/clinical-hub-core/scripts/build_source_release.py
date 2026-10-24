"""Build a deterministic source archive and SPDX file SBOM from the exact committed allowlist."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
from datetime import datetime, timezone


def build(output):
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    git = lambda *args: subprocess.check_output(['git', *args])
    revision = git('rev-parse', 'HEAD').decode().strip()
    epoch = int(git('show', '-s', '--format=%ct', 'HEAD'))
    prefix = git('rev-parse', '--show-prefix').decode().strip()
    names = json.loads(git('show', 'HEAD:' + prefix + 'PUBLIC_SOURCE_FILES.json'))
    tree_names = set(git('ls-tree', '-r', '--name-only', 'HEAD', '--', '.').decode().splitlines())
    if tree_names != set(names) or len(names) != len(set(names)):
        raise ValueError('Committed source allowlist differs from release tree')
    files = []
    archive = output / 'clinical-hub-core.tar'
    with tarfile.open(archive, 'w', format=tarfile.PAX_FORMAT) as tar:
        for index, name in enumerate(sorted(names)):
            if Path(name).is_absolute() or '..' in Path(name).parts:
                raise ValueError('Unsafe source path')
            mode = git('ls-tree', 'HEAD', '--', name).decode().split()[0]
            if mode not in ('100644', '100755'):
                raise ValueError('Release accepts regular text files only')
            data = git('show', f'HEAD:{prefix}{name}')
            data.decode('utf-8')
            member = tarfile.TarInfo('clinical-hub-core/' + name)
            member.size = len(data); member.mtime = epoch; member.mode = 0o755 if mode == '100755' else 0o644
            tar.addfile(member, io.BytesIO(data))
            files.append({'SPDXID': f'SPDXRef-File-{index}', 'fileName': './' + name,
                          'checksums': [{'algorithm': 'SHA256', 'checksumValue': hashlib.sha256(data).hexdigest()},
                                        {'algorithm': 'SHA1', 'checksumValue': hashlib.sha1(data).hexdigest()}],
                          'licenseConcluded': 'NOASSERTION', 'copyrightText': 'NOASSERTION'})
    verification = hashlib.sha1(''.join(sorted(f['checksums'][1]['checksumValue'] for f in files)).encode()).hexdigest()
    sbom = {'spdxVersion': 'SPDX-2.3', 'dataLicense': 'CC0-1.0', 'SPDXID': 'SPDXRef-DOCUMENT',
        'name': 'clinical-hub-core-source',
        'documentNamespace': f'https://github.com/edithatogo/careops/sbom/clinical-hub-core/{revision}',
        'creationInfo': {'created': datetime.fromtimestamp(epoch, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                         'creators': ['Tool: clinical-hub-core-source-builder']},
        'packages': [{'name': 'clinical-hub-core-source', 'SPDXID': 'SPDXRef-Package',
                      'versionInfo': revision, 'downloadLocation': 'NOASSERTION', 'filesAnalyzed': True,
                      'packageVerificationCode': {'packageVerificationCodeValue': verification},
                      'licenseConcluded': 'NOASSERTION', 'licenseDeclared': 'NOASSERTION',
                      'copyrightText': 'NOASSERTION'}], 'files': files,
        'relationships': [{'spdxElementId': 'SPDXRef-DOCUMENT', 'relationshipType': 'DESCRIBES',
                           'relatedSpdxElement': 'SPDXRef-Package'}] +
                         [{'spdxElementId': 'SPDXRef-Package', 'relationshipType': 'CONTAINS',
                           'relatedSpdxElement': f['SPDXID']} for f in files]}
    (output / 'source.spdx.json').write_text(json.dumps(sbom, indent=2) + '\n')
    receipt = {'revision': revision, 'source_files': len(files), 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
               'sbom_sha256': hashlib.sha256((output/'source.spdx.json').read_bytes()).hexdigest(),
               'scope': 'source distribution only; build dependencies are declared in the shipped hash lock, not bundled runtimes'}
    (output/'release.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', required=True)
    print(json.dumps(build(p.parse_args().output)))
