"""Qualify the pinned private Incidents source using disposable fictional inputs.

No tenant operation, real source file, native Power BI engine or child mutation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(module: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(module), *args], text=True, stderr=subprocess.PIPE).strip()


def check_source(module: Path, expected: str) -> None:
    if not module.is_dir() or not (module / '.git').exists():
        raise ValueError('Initialize the optional private Incidents submodule with an authorised Git credential first.')
    if git(module, 'rev-parse', '--show-toplevel') != str(module.resolve()):
        raise ValueError('Expected an independent module checkout.')
    if git(module, 'rev-parse', 'HEAD') != expected:
        raise ValueError('Module revision differs from the reviewed source pin.')
    if git(module, 'status', '--porcelain'):
        raise ValueError('Module has local changes; preserve owner work and use a clean pinned checkout.')


def read_pin() -> dict:
    pin = json.loads((ROOT / 'portfolio/incidents-source.json').read_text())
    inventory = json.loads((ROOT / 'PUBLIC_SOURCE_FILES.json').read_text())
    if inventory['gitlinks'].get(pin['path']) != pin['commit']:
        raise ValueError('Incidents reference differs from the reviewed publication inventory.')
    if pin['visibility'] != 'private' or pin['publicRedistributionQualified'] is not False:
        raise ValueError('Private source must retain its explicit publication boundary.')
    return pin


def validate_structure(result: dict) -> None:
    issues = ['MissingRequiredPaths', 'JsonParseFailures', 'PageTreeIssues', 'SchemaIssues', 'ModelIssues']
    if result.get('Status') != 'Pass' or result.get('PackageExists') is not True or any(result.get(k) != [] for k in issues):
        raise ValueError('Upstream package has structural issues or incomplete results.')


def qualify(module: Path) -> dict:
    pin = read_pin()
    module = module.resolve()
    check_source(module, pin['commit'])
    dashboard = module / 'powerbi/incidents_dashboard'
    # The upstream PowerShell checker returns an object; exit 0 alone is insufficient.
    script = dashboard / 'validation/pbip_integrity_check_v1_20260428.ps1'
    # Use a script file and named arguments, avoiding interpolation of filesystem paths.
    with tempfile.TemporaryDirectory(prefix='careops-incidents-') as tmp:
        temp = Path(tmp)
        wrapper = temp / 'structure.ps1'
        wrapper.write_text("param([string]$Checker,[string]$Dashboard)\n$ErrorActionPreference='Stop'\n$r = & $Checker -RootPath $Dashboard\n$r | ConvertTo-Json -Depth 8 -Compress\n")
        run = subprocess.run(['pwsh', '-NoProfile', '-File', str(wrapper), '-Checker', str(script), '-Dashboard', str(dashboard)], check=True, capture_output=True, text=True)
        structure = json.loads(run.stdout)
        validate_structure(structure)
        source = dashboard / 'scripts/build_surveillance_outputs_v1_20260429.py'
        spec = importlib.util.spec_from_file_location('incidents_surveillance', source)
        if spec is None or spec.loader is None:
            raise ValueError('Unable to load the reviewed surveillance source.')
        builder = importlib.util.module_from_spec(spec)
        previous_bytecode = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(builder)
        finally:
            sys.dont_write_bytecode = previous_bytecode
        fixture = temp / 'fictional.csv'
        with fixture.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=['incident_date', 'details_clean'])
            writer.writeheader()
            for month, total, cohort in [(1, 10, 2), (2, 6, 1), (3, 5, 1)]:
                for n in range(total):
                    writer.writerow({'incident_date': f'2040-{month:02d}-{31 if month in (1,3) else 29:02d}', 'details_clean': 'heparin' if n < cohort else 'fictional fixture'})
        builder.SOURCE_CSV = fixture
        builder.ANALYSIS_START = date(2040, 1, 1)
        builder.ANALYSIS_END = date(2040, 3, 31)
        first = builder.build_rows()
        second = builder.build_rows()
        if first != second:
            raise ValueError('Fictional staging is not deterministic.')
        totals = [int(r['incident_count']) for r in first if r['cohort_key'] == 'all_incidents']
        cohort = [int(r['incident_count']) for r in first if r['cohort_key'] == 'heparin_text_match']
        if totals != [10, 6, 5] or cohort != [2, 1, 1] or len(first) != 6:
            raise ValueError('Fictional source counts or cohort denominators changed.')
        builder.SOURCE_CSV = temp / 'absent.csv'
        try:
            builder.build_rows()
        except FileNotFoundError:
            pass
        else:
            raise ValueError('Missing source was silently accepted.')
        check_source(module, pin['commit'])
        return {'module': pin['repository'], 'commit': pin['commit'], 'scope': 'private-source-structure-and-fictional-staging-only', 'structure': 'passed-all-issue-arrays', 'fictionalRows': len(first), 'repeat': 'identical', 'missingSource': 'refused', 'fixtureDigest': hashlib.sha256(json.dumps(first, sort_keys=True).encode()).hexdigest(), 'nativeRuntimeVerified': False, 'privacySuppressionVerified': False, 'realDataRead': False, 'tenantWrites': False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module-root', type=Path, default=ROOT / 'modules/careops-incidents')
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--check-pin', action='store_true', help='Validate parent metadata without accessing private source')
    args = parser.parse_args()
    if args.check_pin:
        read_pin()
        print('Incidents private source reference matches reviewed inventory; no child checkout required.')
        return
    result = qualify(args.module_root)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
