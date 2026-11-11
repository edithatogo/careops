"""Generate PowerShell list provisioning statements from reviewed logical model.

Does not deploy or set production ACLs. Execute in a controlled dev tenant only.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
model=json.loads((ROOT/'config/data-model.json').read_text())
assert len({x['name'] for x in model['lists']})==len(model['lists'])
assert all(x['name'].startswith('JP_') and x['key']=='Key' for x in model['lists'])
lines=['#Requires -Version 7.2', '# Generated development-only provisioning. NO ACL or production authority.',
  "[CmdletBinding(SupportsShouldProcess=$true,ConfirmImpact='High')]",
  "param([Parameter(Mandatory)][string]$SiteUrl,[Parameter(Mandatory)][guid]$ClientId)",
  "$ErrorActionPreference='Stop'", "Import-Module PnP.PowerShell -ErrorAction Stop",
  "if ($SiteUrl -notmatch '^https://[^/]+\\.sharepoint\\.com/sites/[^/]+$') { throw 'Invalid site URL' }",
  "if ($WhatIfPreference) { Write-Host 'WhatIf: dry run; do not provision'; return }",
  "Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Interactive",'try {']
for item in model['lists']:
    name=item['name']
    lines += [f"  # {name} - data boundary {item['boundary']}",
      f"  if (-not (Get-PnPList -Identity '{name}' -ErrorAction SilentlyContinue)) {{",
      f"    if ($PSCmdlet.ShouldProcess('{name}','Create list')) {{ New-PnPList -Title '{name}' -Template GenericList -OnQuickLaunch:$false | Out-Null }}",
      '  }',
      f"  if (-not (Get-PnPField -List '{name}' -Identity 'Key' -ErrorAction SilentlyContinue)) {{",
      f"    if ($PSCmdlet.ShouldProcess('{name}','Add unique Key')) {{ Add-PnPField -List '{name}' -DisplayName 'Key' -InternalName 'Key' -Type Text | Out-Null }}",
      '  }',
      f"  if (-not (Get-PnPField -List '{name}' -Identity 'Payload' -ErrorAction SilentlyContinue)) {{",
      f"    if ($PSCmdlet.ShouldProcess('{name}','Add Payload')) {{ Add-PnPField -List '{name}' -DisplayName 'Payload' -InternalName 'Payload' -Type Note | Out-Null }}",
      '  }',
      f"  if ($PSCmdlet.ShouldProcess('{name}','Unique index and versioning')) {{",
      f"    Set-PnPField -List '{name}' -Identity 'Key' -Values @{{Indexed=$true;EnforceUniqueValues=$true}} | Out-Null",
      f"    Set-PnPList -Identity '{name}' -EnableVersioning $true -MajorVersions 100 | Out-Null",
      '  }']
    for field in item['fields']:
        if field in ('Title','Payload','Key'):continue
        type_='Number' if field in ('Generation','RuleVersion','WeekIndex') else 'DateTime' if field.endswith(('At','From','To')) else 'Text'
        lines += [f"  if (-not (Get-PnPField -List '{name}' -Identity '{field}' -ErrorAction SilentlyContinue)) {{",
        f"    if ($PSCmdlet.ShouldProcess('{name}','Add {field}')) {{ Add-PnPField -List '{name}' -DisplayName '{field}' -InternalName '{field}' -Type {type_} | Out-Null }}",'  }']
    lines +=[f"  $field=Get-PnPField -List '{name}' -Identity 'Key'",f"  if (-not $field.Indexed -or -not $field.EnforceUniqueValues) {{ throw 'Missing unique Key for {name}' }}"]
lines += ['} finally { Disconnect-PnPOnline -ErrorAction SilentlyContinue }',
 "Write-Warning 'DEVELOPMENT SCHEMA ONLY: explicit ACL/retention/records configuration pending. Never load real staff data.'"]
out=ROOT/'deploy'/'provision-sharepoint-development.ps1';out.write_text('\n'.join(lines)+'\n')
print('generated',len(model['lists']),'list scaffolds in',out)
