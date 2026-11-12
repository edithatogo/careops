[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$tokens = $null
$errors = $null
$source = Join-Path $PSScriptRoot 'New-LocalDeploymentSettings.ps1'
$tree = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$errors)
if (@($errors).Count -ne 0) { throw 'Settings source does not parse.' }
$functions = @($tree.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Select-ConnectionForApi' }, $true))
if ($functions.Count -ne 1) { throw 'Expected one connection selector.' }
# Execute only the pure selection function, never the native-reading script body.
$select = $functions[0].Body.GetScriptBlock()
$api = '/providers/Microsoft.PowerApps/apis/shared_teams'
$approved = [pscustomobject]@{ ApiId=$api; Name='approved@example.invalid'; Status='Connected'; Id='fixture-approved' }
$other = [pscustomobject]@{ ApiId=$api; Name='other@example.invalid'; Status='Connected'; Id='fixture-other' }
$chosen = @(& $select -Connections @($other, $approved) -ApiName 'shared_teams' -PreferredName 'approved@example.invalid')
if ($chosen.Count -ne 1 -or $chosen[0].Id -ne 'fixture-approved') { throw 'Approved account was not selected exactly.' }
foreach ($rows in @(@($other), @($other, [pscustomobject]@{ ApiId=$api; Name='approved@example.invalid'; Status='Disconnected'; Id='fixture-offline' }))) {
    $refused = $false
    try { & $select -Connections $rows -ApiName 'shared_teams' -PreferredName 'approved@example.invalid' | Out-Null }
    catch { if ($_.Exception.Message -ne 'No connected approved account for the requested connector.') { throw }; $refused = $true }
    if (-not $refused) { throw 'Selector fell back to an unapproved connection.' }
}
Write-Host 'Private connection selector: exact approved selection and both refusal cases passed; no native calls.'
