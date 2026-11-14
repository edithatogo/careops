#Requires -Version 7.2
<#
.SYNOPSIS
  Idempotent *development-only* SharePoint list provisioning.
.DESCRIPTION
  Uses PnP.PowerShell with an approved interactive Entra application.
  No credentials, tenant IDs or employee data are embedded in source.
  Run -WhatIf first. Does not assign permissions or enable production use.
#>
[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
param(
  [Parameter(Mandatory=$true)][ValidatePattern('^https://[^/]+\.sharepoint\.com/sites/[^/]+$')][string]$SiteUrl,
  [Parameter(Mandatory=$true)][guid]$ClientId,
  [string]$Prefix='JP_'
)
$ErrorActionPreference = 'Stop'
Import-Module PnP.PowerShell -ErrorAction Stop
if ($Prefix -notmatch '^[A-Za-z][A-Za-z0-9_]{0,30}$') { throw 'Invalid list prefix' }
$names = @('PlanHeads','Operations','Artifacts','ReviewObligations')
if ($WhatIfPreference) {
  foreach ($name in $names) { Write-Host "[WhatIf] Provision $Prefix$name with unique Key and Payload" }
  return
}
Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Interactive
try {
  foreach ($name in $names) {
    $title = "$Prefix$name"
    $list = Get-PnPList -Identity $title -ErrorAction SilentlyContinue
    if (-not $list) {
      if ($PSCmdlet.ShouldProcess($title, 'Create restricted generic list')) {
        New-PnPList -Title $title -Template GenericList -OnQuickLaunch:$false | Out-Null
      }
    }
    $list = Get-PnPList -Identity $title -ErrorAction Stop
    foreach ($field in @(
      @{DisplayName='Key';InternalName='Key';Type='Text'},
      @{DisplayName='Payload';InternalName='Payload';Type='Note'}
    )) {
      $existing = Get-PnPField -List $title -Identity $field.InternalName -ErrorAction SilentlyContinue
      if (-not $existing -and $PSCmdlet.ShouldProcess($title, "Add $($field.InternalName)")) {
        Add-PnPField -List $title -DisplayName $field.DisplayName -InternalName $field.InternalName -Type $field.Type | Out-Null
      }
    }
    # Unique values require an indexed text column. Fail if SharePoint refuses.
    if ($PSCmdlet.ShouldProcess($title, 'Enforce unique indexed Key')) {
      Set-PnPField -List $title -Identity 'Key' -Values @{Indexed=$true;EnforceUniqueValues=$true} | Out-Null
      Set-PnPList -Identity $title -EnableVersioning $true -MajorVersions 100 | Out-Null
    }
    $key = Get-PnPField -List $title -Identity 'Key'
    if (-not $key.Indexed -or -not $key.EnforceUniqueValues) { throw "$title missing required unique indexed Key" }
    Write-Host "Verified $title"
  }
  Write-Warning 'Provisioning does not configure role ACLs, records retention or native cloud flows. Do not store real staff data yet.'
} finally {
  Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
