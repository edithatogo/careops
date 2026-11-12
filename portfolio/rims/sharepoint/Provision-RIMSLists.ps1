<# Dry-run-first source-only PnP SharePoint List recreation helper.
Existing lists are never modified, sensitive lists are always refused for
automatic creation, and no tenant connection occurs without explicit -Apply. #>
param([string]$SiteUrl,[string]$ClientId,[string]$ApprovedPlanPath,[switch]$Apply)
$ErrorActionPreference="Stop"
$path=Join-Path $PSScriptRoot "lists.recreation.json"
$spec=Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
$sensitive=@("PersonAffiliations","ReviewDecisions")
if (-not $Apply) {
  Write-Output "RIMS DRY RUN: no connection, creation or mutation"
  foreach($entry in $spec.lists.PSObject.Properties){
    Write-Output ("List: "+$entry.Name)
    foreach($col in $entry.Value.columns.PSObject.Properties){
      Write-Output ("  "+$col.Name+" : "+$col.Value.type)
    }
  }
  return
}
if([string]::IsNullOrWhiteSpace($SiteUrl) -or [string]::IsNullOrWhiteSpace($ClientId) -or [string]::IsNullOrWhiteSpace($ApprovedPlanPath)){
  throw "SiteUrl, tenant-approved ClientId and reviewed private plan are required"
}
$approved=Get-Content -LiteralPath $ApprovedPlanPath -Raw | ConvertFrom-Json
if($approved.schema -ne "careops-rims.approved-provision-plan/1" -or $approved.site_url -ne $SiteUrl -or $approved.authorised -ne $true){
  throw "Invalid site-specific approval plan"
}
foreach($title in $approved.create_missing_lists){
  if($sensitive -contains $title){throw "Sensitive List requires separate owner-qualified security/retention provisioning"}
  if($null -eq $spec.lists.$title){throw "Unknown list requested"}
}
$connection=Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Interactive -ReturnConnection
foreach($title in $approved.create_missing_lists){
  $existing=Get-PnPList -Identity $title -Connection $connection -ErrorAction SilentlyContinue
  if($null -ne $existing){throw "Existing list detected: reconcile GUID; do not duplicate"}
  New-PnPList -Title $title -Template GenericList -EnableVersioning -Connection $connection | Out-Null
  foreach($col in $spec.lists.$title.columns.PSObject.Properties){
    $f=$col.Value
    if($f.type -eq "Choice"){
      Add-PnPField -List $title -DisplayName $f.display_name -InternalName $f.internal_name -Type Choice -Choices ([string[]]$f.choices) -Connection $connection | Out-Null
    }else{
      Add-PnPField -List $title -DisplayName $f.display_name -InternalName $f.internal_name -Type $f.type -Connection $connection | Out-Null
    }
  }
  Set-PnPList -Identity $title -EnableVersioning $true -Connection $connection | Out-Null
  Write-Output "Created empty List: verify permissions/indexes/views before admission"
}
