"""Build an auditable, synthetic-only *source* ZIP; not a Power Platform solution ZIP."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import json, os, sys

ROOT=Path(__file__).resolve().parents[1]
REJECT={'.doc','.docx','.pdf','.xlsx','.xls','.xlsm','.ppt','.pptx','.pbix','.msapp','.db','.sqlite3','.pyc','.zip','.env'}
ALLOW={'.py','.json','.yaml','.md','.ps1','.sh','.txt','.yml'}

def build(output):
    output=Path(output).resolve()
    if output.is_relative_to(ROOT):raise ValueError('release must be outside source tree')
    files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(d.startswith('.') or d=='__pycache__' for d in p.relative_to(ROOT).parts[:-1]):continue
        if p.name.startswith('.') or p.suffix in REJECT:continue
        if p.suffix not in ALLOW:raise ValueError('unknown source type: '+str(p))
        contents=p.read_bytes()
        # Private data protection: no source bytes resembling personally sensitive identifiers.
        if p.name != 'build_release.py' and any(x in contents for x in (b'M Mantha',b'IMECYS Medical Staff Job Planning (Draft)',b'Staff ID')):
            raise ValueError('restricted reference marker in public source')
        files.append((p.relative_to(ROOT).as_posix(), contents))
    records=[{'path':p,'sha256':sha256(data).hexdigest(),'bytes':len(data)} for p,data in sorted(files)]
    manifest={'type':'careops-workforce-job-planning-source-only','version':'0.4.0-offline',
              'native_power_platform_import_verified':False,'sharepoint_tenant_tests_verified':False,
              'contents':records}
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for p,data in sorted(files):z.writestr('careops-workforce-app/'+p,data)
        z.writestr('SOURCE-MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with ZipFile(output) as z:
        if z.testzip():raise ValueError('ZIP integrity failure')
    return {'zip':str(output),'files':len(files),'sha256':sha256(output.read_bytes()).hexdigest(),
            'native_import':'not verified'}

if __name__=='__main__':
    if len(sys.argv)!=2:sys.exit('usage: python tools/build_release.py /mnt/data/source.zip')
    print(json.dumps(build(sys.argv[1]),indent=2))
