"""Offline source contract qualification. No cloud calls and no confidential data."""
from pathlib import Path
import json, re, ast, sys, unittest
import yaml
ROOT=Path(__file__).resolve().parents[1]

BLOCKED={'.doc','.docx','.pdf','.xlsx','.xls','.xlsm','.ppt','.pptx','.msapp','.pbix','.pbit'}

def audit():
    problems=[]
    for f in ROOT.rglob('*'):
        if not f.is_file():continue
        rel=f.relative_to(ROOT).as_posix()
        if f.suffix.lower() in BLOCKED:problems.append('disallowed confidential/binary format: '+rel)
        if any(x in rel.lower() for x in ('__pycache__','.sqlite','.db','.env','/private/')):continue
        if f.suffix=='.py':
            try:ast.parse(f.read_text())
            except Exception as e:problems.append(f'{rel}: {e}')
        elif f.name.endswith('.pa.yaml'):
            try:
                obj=yaml.safe_load(f.read_text())
                if not isinstance(obj,dict) or not ('App' in obj or 'Screens' in obj):raise ValueError('not an app/screen definition')
            except Exception as e:problems.append(f'{rel}: {e}')
        elif f.suffix=='.json':
            try:
                obj=json.loads(f.read_text())
                if f.name.endswith('.workflow.json'):
                    if obj['contentVersion']!='0.1.0.0' or not obj.get('_implementationStatus','').startswith('binding-required'):
                        raise ValueError('flow contract incorrectly claims operational status')
                    if not obj.get('triggers') or not obj.get('actions'):raise ValueError('workflow definition incomplete')
            except Exception as e:problems.append(f'{rel}: {e}')
        if f.suffix in ('.json','.yaml','.md','.py','.ps1'):
            text=f.read_text(errors='replace')
            if re.search(r'(?i)(Bearer\s+[A-Za-z0-9._-]{20,}|password\s*=\s*["\'][^"\']{6}|-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)',text):
                problems.append('credential-like string: '+rel)
    expected=10
    workflows=list((ROOT/'flows').glob('*.workflow.json'))
    if len(workflows)!=expected:problems.append(f'Expected {expected} flow definitions; got {len(workflows)}')
    # Additional read-only WDL candidates are separate from the ten intentionally
    # disabled privileged workflow scaffolds; static inspection is not cloud import.
    candidates=list((ROOT/'flows/native-candidates').glob('*.json'))
    if len(candidates)!=3:problems.append(f'Expected three read-only monitor candidates; got {len(candidates)}')
    for p in candidates:
        try:
            d=json.loads(p.read_text())
            if set(d)!={'$schema','contentVersion','parameters','triggers','actions','outputs'}:
                raise ValueError('unexpected WDL top-level key')
            if any(a.get('type')=='OpenApiConnection' and
                   (a.get('inputs',{}).get('host',{}).get('operationId')!='HttpRequest' or
                    a.get('inputs',{}).get('parameters',{}).get('parameters/method')!='GET')
                   for a in d['actions'].values()):
                raise ValueError('candidate contains a non-read-only connector action')
        except (ValueError,KeyError,TypeError) as exc:
            problems.append(f'{p.name}: {exc}')
    if problems:raise ValueError('\n'.join(problems))
    return {'static_audit':'pass','screens':len(list((ROOT/'canvas/Src').glob('*.pa.yaml')))-1,'flows':len(workflows),'read_only_monitor_candidates':len(candidates),
            'native_import':'unverified','workflows_operational':False}
if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
