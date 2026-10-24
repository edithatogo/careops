import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import re
import shlex
import pytest
from scripts.ci_candidate import resolve, versions
from scripts.build_source_release import build


def test_renovate_discovers_compiled_lock_and_its_input():
    config = json.loads(Path('renovate.json').read_text())
    patterns = config['pip-compile']['managerFilePatterns']
    assert any(re.search(pattern[1:-1], 'requirements-dev.lock') for pattern in patterns)
    assert config['pip_requirements']['enabled'] is False
    command = Path('requirements-dev.lock').read_text().splitlines()[1].removeprefix('#    ')
    args = shlex.split(command)
    assert args[:4] == ['uv', 'pip', 'compile', 'requirements-dev.txt']
    assert '--generate-hashes' in args
    assert '--output-file=requirements-dev.lock' in args
    assert '--python-version=' + Path('.python-version').read_text().strip() in args
    # Renovate's parser requires equals syntax for options with arguments.
    assert not {'--output-file', '--python-version', '--prerelease'} & set(args)
    runtime_rule = next(rule for rule in config['packageRules']
                        if rule.get('matchFileNames') == ['.python-version'])
    allowed = re.compile(runtime_rule['allowedVersions'][1:-1])
    assert allowed.search('3.15.1') and not allowed.search('3.16.0a1')


def test_lock_versions_satisfy_declared_inputs():
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name
    pins = {canonicalize_name(k): v for k, v in versions(Path('requirements-dev.lock').read_text()).items()}
    for line in Path('requirements-dev.txt').read_text().splitlines():
        if line.strip() and not line.startswith('#'):
            requirement = Requirement(line)
            assert requirement.specifier.contains(pins[canonicalize_name(requirement.name)], prereleases=True)


def test_resolution_failure_retains_receipt_and_baseline(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path); Path('requirements-dev.lock').write_text('baseline')
    monkeypatch.setattr(subprocess, 'check_output', lambda *a, **k: 'uv 0.13.1')
    def fail(*a, **k):
        raise subprocess.CalledProcessError(1, ['uv'])
    monkeypatch.setattr(subprocess, 'run', fail)
    with pytest.raises(subprocess.CalledProcessError): resolve('candidate', preview=True)
    receipt = json.loads(Path('candidate/receipt.json').read_text())
    assert receipt['status'] == 'resolution_failed' and receipt['baseline_unchanged']
    with pytest.raises(ValueError): resolve('candidate')


def test_release_sbom_exactly_matches_shipped_committed_bytes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(['git', 'init', '-q'], check=True)
    Path('example.py').write_text('# fictional source\n')
    Path('PUBLIC_SOURCE_FILES.json').write_text(json.dumps(['example.py', 'PUBLIC_SOURCE_FILES.json']))
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                    'commit', '-qm', 'fictional'], check=True)
    receipt = build('release')
    sbom = json.loads(Path('release/source.spdx.json').read_text())
    with tarfile.open('release/clinical-hub-core.tar') as archive:
        assert len(archive.getmembers()) == receipt['source_files'] == 2
        for item in sbom['files']:
            data = archive.extractfile('clinical-hub-core/' + item['fileName'][2:]).read()
            assert hashlib.sha256(data).hexdigest() == item['checksums'][0]['checksumValue']
    assert build('repeat')['archive_sha256'] == receipt['archive_sha256']
    Path('extra.txt').write_text('fictional unlisted file')
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                    'commit', '-qm', 'extra'], check=True)
    with pytest.raises(ValueError): build('rejected')


def test_nested_module_release_excludes_parent_and_rejects_unlisted_module_file(tmp_path, monkeypatch):
    parent = tmp_path / 'parent'
    module = parent / 'modules' / 'meeting'
    module.mkdir(parents=True)
    subprocess.run(['git', 'init', '-q', str(parent)], check=True)
    (parent / 'parent-only.txt').write_text('parent source, outside this release')
    (module / 'example.py').write_text('# fictional module\n')
    (module / 'PUBLIC_SOURCE_FILES.json').write_text(json.dumps(['example.py', 'PUBLIC_SOURCE_FILES.json']))
    subprocess.run(['git', '-C', str(parent), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(parent), '-c', 'user.name=Fixture', '-c',
                    'user.email=fixture@example.invalid', 'commit', '-qm', 'nested fixture'], check=True)
    monkeypatch.chdir(module)
    from scripts.validate_public_source import validate
    assert validate(module) == []
    assert build('release')['source_files'] == 2
    with tarfile.open('release/clinical-hub-core.tar') as archive:
        assert {entry.name for entry in archive} == {
            'clinical-hub-core/example.py', 'clinical-hub-core/PUBLIC_SOURCE_FILES.json'}
    (module / 'unreviewed.txt').write_text('fictional unreviewed source')
    subprocess.run(['git', 'add', 'unreviewed.txt'], check=True)
    assert any('Unreviewed tracked path' in error for error in validate(module))
    subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                    'commit', '-qm', 'unreviewed'], check=True)
    with pytest.raises(ValueError, match='allowlist'):
        build('rejected')
