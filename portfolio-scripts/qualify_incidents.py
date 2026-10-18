"""Qualify the integrated public Incidents source using disposable fictional inputs.

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


def check_source(module: Path, expected: str) -> None:
    if not module.is_dir() or (module / '.git').exists():
        raise ValueError('Expected ordinary integrated module files, not an independent checkout.')
    provenance_path = module / 'SOURCE_PROVENANCE.json'
    if not provenance_path.is_file():
        raise ValueError('Missing reviewed module provenance.')
    provenance = json.loads(provenance_path.read_text())
    if provenance['sourceCommit'] != expected:
        raise ValueError('Source provenance differs from the reviewed migration baseline.')
    for item in provenance['files']:
        path = module / item['path']
        if not path.resolve().is_relative_to(module.resolve()) or path.is_symlink() or not path.is_file():
            raise ValueError('Missing or unsafe integrated source path.')
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Module source differs from its reviewed inventory; review and update provenance.')


def read_pin() -> dict:
    pin = json.loads((ROOT / 'portfolio/incidents-source.json').read_text())
    inventory = json.loads((ROOT / 'PUBLIC_SOURCE_FILES.json').read_text())
    if pin['path'] in inventory['gitlinks'] or pin['scope'] != 'integrated-public-source':
        raise ValueError('Incidents must be integrated source, not a private gitlink.')
    if pin['visibility'] != 'public' or pin['publicRedistributionQualified'] is not True:
        raise ValueError('Integrated source must retain its reviewed publication boundary.')
    required = [pin['path'] + '/' + name for name in ['LICENSE', 'README.md', 'SOURCE_PROVENANCE.json']]
    if any(name not in inventory['files'] for name in required):
        raise ValueError('Module source is missing from the publication inventory.')
    check_source(ROOT / pin['path'], pin['commit'])
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
        return {'module': pin['repository'], 'commit': pin['commit'], 'scope': 'integrated-source-structure-and-fictional-staging-only', 'structure': 'passed-all-issue-arrays', 'fictionalRows': len(first), 'repeat': 'identical', 'missingSource': 'refused', 'fixtureDigest': hashlib.sha256(json.dumps(first, sort_keys=True).encode()).hexdigest(), 'nativeRuntimeVerified': False, 'privacySuppressionVerified': False, 'realDataRead': False, 'tenantWrites': False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module-root', type=Path, default=ROOT / 'modules/careops-incidents')
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--check-pin', action='store_true', help='Validate integrated source inventory')
    args = parser.parse_args()
    if args.check_pin:
        read_pin()
        print('Incidents integrated source matches reviewed inventory; no private checkout required.')
        return
    result = qualify(args.module_root)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
