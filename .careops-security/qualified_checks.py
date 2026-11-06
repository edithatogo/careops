# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0

"""Private-compatible source and dependency gates; never upload source or findings."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / '.local/security-tools'
RULES_COMMIT = 'f1d2b562b414783763fd02a6ed2736eaed622efa'
RULES_SHA = '9a5f1cd5c625418cc1c776120123e2d4371df9bb66e099426b17c3488e13619d'
ASSETS = {
    'Darwin': {
        'core': ('opengrep-core_osx_aarch64.tar.gz', 'cce019aba35ba0c79f74b22fc9e2f8562ca651d76d5a04d7dcc440f967e45930'),
        'osv': ('osv-scanner_darwin_arm64', 'd4926ef8da134332543be276dff157e4c170f99ad91fc48e89448a8816bdf70b'),
    },
    'Linux': {
        'core': ('opengrep-core_linux_x86.tar.gz', '1a78593c369cd58a8545a1dfb2ce548139f028a1af4ea7d08bc5ce8385cde243'),
        'osv': ('osv-scanner_linux_amd64', '160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b'),
    },
}


def execute(command: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, capture_output=True, timeout=600, check=False)


def tracked(root: Path) -> list[str]:
    result = execute(['git', 'ls-files', '-z'], cwd=root)
    if result.returncode:
        raise ValueError('tracked-file selection failed')
    return [name for name in result.stdout.decode().split('\0') if name and (root / name).is_file()]


def fetch(url: str, digest: str, destination: Path) -> bytes:
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in {'github.com', 'codeload.github.com'} or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('unqualified asset origin')
    if destination.exists():
        data = destination.read_bytes()
    else:
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read(150 * 1024 * 1024 + 1)
        if len(data) > 150 * 1024 * 1024:
            raise ValueError('tool asset exceeds bounded size')
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('tool asset digest mismatch')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_bytes(data)
    return data


def native(kind: str) -> Path:
    system, machine = platform.system(), platform.machine()
    if (system, machine) not in {('Darwin', 'arm64'), ('Linux', 'x86_64')}:
        raise ValueError('unqualified native tool platform')
    name, digest = ASSETS[system][kind]
    project, version = ('opengrep/opengrep', 'v1.33.1') if kind == 'core' else ('google/osv-scanner', 'v2.7.0')
    data = fetch(f'https://github.com/{project}/releases/download/{version}/{name}', digest, TOOLS / name)
    target = TOOLS / ('qualified-core' if kind == 'core' else 'qualified-osv')
    if kind == 'core':
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            members = [m for m in archive.getmembers() if m.name == 'opengrep-core' and m.isfile()]
            if len(members) != 1:
                raise ValueError('unexpected native engine archive')
            payload = archive.extractfile(members[0]).read()
            if not target.exists() or target.read_bytes() != payload:
                target.write_bytes(payload)
    else:
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
    target.chmod(0o700)
    return target


def rule_config(language: str) -> tuple[Path, int]:
    archive = fetch(f'https://codeload.github.com/opengrep/opengrep-rules/tar.gz/{RULES_COMMIT}', RULES_SHA, TOOLS / 'qualified-rules.tar.gz')
    rules = []
    with tarfile.open(fileobj=io.BytesIO(archive)) as package:
        for member in sorted(package.getmembers(), key=lambda m: m.name):
            path = Path(member.name)
            if not member.isfile() or not member.name.endswith('.yaml') or f'/{language}/' not in member.name or '/security/' not in member.name:
                continue
            for rule in yaml.safe_load(package.extractfile(member).read()).get('rules', []):
                rule['id'] = '.'.join(path.parts[1:]).removesuffix('.yaml') + '.' + rule['id']
                rules.append(rule)
    if not rules:
        raise ValueError('missing upstream security rules')
    config = TOOLS / (language + '-qualified-rules.yaml')
    config.write_text(yaml.safe_dump({'rules': rules}, sort_keys=False))
    return config, len(rules)


def review_key(path: str, rule: str, line: int, root: Path) -> tuple[str, str, int, str]:
    relative = Path(path).as_posix().removeprefix('./')
    return relative, rule, line, hashlib.sha256((root / relative).read_bytes()).hexdigest()


def analyze_source(root: Path) -> dict:
    paths = tracked(root)
    python = [p for p in paths if p.endswith('.py')]
    report = root / '.local/security-source-bandit.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    result = execute([sys.executable, '-m', 'bandit', '-c', str(ROOT / '.careops-security/bandit.yaml'), '--exclude', '', '--ignore-nosec', '-f', 'json', '-o', str(report), '--', *python], cwd=root)
    if result.returncode not in (0, 1):
        raise ValueError('python source analysis failed')
    bandit = json.loads(report.read_text())
    if bandit.get('errors') or len([p for p in bandit['metrics'] if p != '_totals']) != len(python):
        raise ValueError('incomplete python source analysis')
    findings = [(x['filename'], 'bandit:' + x['test_id'], x['line_number']) for x in bandit['results'] if x['issue_severity'] in ('MEDIUM', 'HIGH')]
    core, parser_gaps, core_counts = native('core'), [], {}
    for language, extensions in [('python', {'.py'}), ('javascript', {'.js', '.mjs'}), ('typescript', {'.ts'})]:
        selected = [p for p in paths if Path(p).suffix in extensions]
        if not selected:
            continue
        config, count = rule_config(language)
        target_file = TOOLS / (language + '-qualified-targets.json')
        target_file.write_text(json.dumps([['CodeTarget', {'path':str(root / p), 'analyzer':language, 'products':['sast']}] for p in selected]))
        result = execute([str(core), '-json_nodots', '-j', '2', '-timeout', '10', '-max_memory', '3000', '-rules', str(config), '-targets', str(target_file)], cwd=root)
        if result.returncode:
            raise ValueError('native source analysis failed')
        value = json.loads(result.stdout)
        (root / ('.local/security-source-' + language + '.json')).write_text(json.dumps(value))
        if value.get('skipped_rules') or len(value.get('rules_by_engine', [])) != count:
            raise ValueError('incomplete native rule execution')
        if {str(Path(p).resolve()) for p in value['paths']['scanned']} != {str((root / p).resolve()) for p in selected}:
            raise ValueError('incomplete native target execution')
        core_counts[language] = {'targets':len(selected), 'rules':count, 'errors':len(value['errors'])}
        for error in value['errors']:
            kind = error.get('error_type')
            kind = kind[0] if isinstance(kind, list) else kind
            if kind not in ('Syntax error', 'PartialParsing'):
                raise ValueError('native scanner execution error')
            path = Path(error['location']['path']).relative_to(root).as_posix()
            # Python 3.15 AST coverage is mandatory and provided by Bandit above.
            # The additional native parser's coverage is reported independently.
            if language != 'python':
                parser_gaps.append(path)
        for finding in value['results']:
            path = Path(finding['path']).relative_to(root).as_posix()
            findings.append((path, finding['check_id'], finding['start']['line']))
    return {'pythonAstFiles':len(python), 'pythonParserErrors':0, 'nativeCoverage':core_counts, 'nonPythonParserGaps':sorted(set(parser_gaps)), 'findings':findings}


def qualify_source_engines() -> None:
    with tempfile.TemporaryDirectory(prefix='security-positive-') as folder:
        directory = Path(folder)
        unsafe = directory / 'unsafe.py'
        unsafe.write_text('eval(untrusted_input)\n')
        report = directory / 'bandit.json'
        result = execute([sys.executable, '-m', 'bandit', '--ignore-nosec', '-f', 'json', '-o', str(report), str(unsafe)])
        value = json.loads(report.read_text())
        if result.returncode != 1 or not any(x['test_id'] == 'B307' for x in value['results']):
            raise ValueError('python positive control was not detected')
        config, _ = rule_config('javascript')
        core = native('core')
        for dangerous in (True, False):
            sample = directory / 'sample.js'
            sink = 'innerHTML' if dangerous else 'textContent'
            sample.write_text('document.body.' + sink + ' = window.location.hash;\n')
            result = execute([str(core), '-json_nodots', '-rules', str(config), '-lang', 'javascript', str(sample)])
            value = json.loads(result.stdout)
            detected = any('insecure-innerhtml' in row['check_id'] for row in value['results'])
            if result.returncode or value['errors'] or detected != dangerous:
                raise ValueError('native positive/negative controls failed')


def check_source(base: str | None) -> None:
    qualify_source_engines()
    current = analyze_source(ROOT)
    baseline = {'findings': [], 'nonPythonParserGaps': []}
    unchanged = set()
    if base:
        if len(base) != 40 or any(c not in '0123456789abcdef' for c in base):
            raise ValueError('explicit immutable source base required')
        with tempfile.TemporaryDirectory(prefix='source-security-base-') as tmp:
            previous = Path(tmp)
            archive = execute(['git', 'archive', base])
            if archive.returncode:
                raise ValueError('base source unavailable')
            with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as package:
                package.extractall(previous, filter='data')
            execute(['git', 'init', '-q'], cwd=previous)
            execute(['git', 'add', '-f', '--', '.'], cwd=previous)
            baseline = analyze_source(previous)
            for path in tracked(ROOT):
                if (previous / path).is_file() and (previous / path).read_bytes() == (ROOT / path).read_bytes():
                    unchanged.add(path)
    policy = json.loads((ROOT / '.careops-security/source-security-reviewed.json').read_text())
    reviews = {(x['path'], x['rule'], x['line'], x['sha256']) for x in policy['findings'] if x.get('reason') and x.get('reviewer')}
    old = {tuple(x) for x in baseline['findings']}
    new = [x for x in current['findings'] if not (x[0].removeprefix('./') in unchanged and tuple(x) in old) and review_key(*x, ROOT) not in reviews]
    gaps = [p for p in current['nonPythonParserGaps'] if p not in unchanged or p not in baseline['nonPythonParserGaps']]
    receipt = {**current, 'findings':len(current['findings']), 'unreviewedNewFindings':len(new), 'unchangedBaselineFindings':sum(x[0].removeprefix('./') in unchanged and tuple(x) in old for x in current['findings']), 'newParserGaps':len(gaps), 'codeqlExecuted':False, 'base':base, 'passed':not new and not gaps}
    (ROOT / '.local/source-security-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
    for path, rule, line in new:
        print(f'Unreviewed source finding: {path}:{line} {rule}')
    if new or gaps:
        raise ValueError('source security review required')


def check_dependencies() -> None:
    paths = tracked(ROOT)
    selected = []
    for path in paths:
        if '/.careops-security/upstream/' in path or '/.careops-security/shared/' in path:
            continue  # Immutable historical tool snapshots, not active dependency locks.
        name = Path(path).name
        if name.startswith('requirements') and name.endswith('.lock'):
            selected.append(('requirements.txt:', path))
        elif name in ('uv.lock', 'Cargo.lock', 'package-lock.json', 'packages.lock.json'):
            selected.append(('', path))
    if not selected:
        raise ValueError('no active locks selected')
    with tempfile.TemporaryDirectory(prefix='dependency-positive-') as folder:
        sample = Path(folder) / 'requirements.txt'
        sample.write_text('django==1.2\n')
        control = Path(folder) / 'control.json'
        result = execute([str(native('osv')), 'scan', 'source', '--lockfile='+str(sample), '--format=json', '--output-file='+str(control)])
        data = json.loads(control.read_text())
        if result.returncode != 1 or not any(p.get('vulnerabilities') for r in data['results'] for p in r['packages']):
            raise ValueError('dependency positive control was not detected')
    report = ROOT / '.local/dependency-vulnerability-review.json'
    result = execute([str(native('osv')), 'scan', 'source', '--format=json', '--all-packages', '--output-file='+str(report), *['--lockfile='+kind+path for kind, path in selected]])
    if result.returncode not in (0, 1) or not report.is_file():
        raise ValueError('dependency scan unavailable')
    value = json.loads(report.read_text())
    scanned = {str(Path(x['source']['path']).resolve()) for x in value.get('results', [])}
    if value.get('errors') or scanned != {str((ROOT / path).resolve()) for _, path in selected}:
        raise ValueError('dependency scan incomplete')
    vulnerable = [(p['package']['name'],p['package']['version']) for r in value['results'] for p in r['packages'] if p.get('vulnerabilities')]
    receipt = {'locks':len(selected), 'vulnerablePackages':vulnerable, 'passed':result.returncode == 0 and not vulnerable, 'nativeDependencyReviewExecuted':False}
    print(json.dumps(receipt))
    if not receipt['passed']:
        raise ValueError('dependency vulnerability review failed')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['source', 'dependencies'])
    parser.add_argument('--base')
    args = parser.parse_args()
    if platform.python_version() != '3.15.1' or sys.prefix == sys.base_prefix or not Path(sys.prefix).resolve().is_relative_to(ROOT):
        raise ValueError('verified repository-local python 3.15.1 required')
    TOOLS.mkdir(parents=True, exist_ok=True)
    if args.mode == 'source':
        check_source(args.base)
    else:
        check_dependencies()
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired, json.JSONDecodeError):
        print('Qualified security gate refused execution or findings; raw diagnostics withheld.', file=sys.stderr)
        raise SystemExit(1)
