[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$scriptPath = Join-Path $repoRoot "scripts\New-AcceptanceEvidenceTemplate.ps1"

function Assert-Condition {
    param(
        [bool] $Condition,
        [string] $Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

Assert-Condition (Test-Path -LiteralPath $scriptPath) "Missing acceptance evidence template script: $scriptPath"

$json = & $scriptPath -Dashboard Both -Format Json
$payload = $json | ConvertFrom-Json

$requiredChecks = @(
    "VMO-ACC-001",
    "VMO-ACC-012",
    "MS-SAMPLE-01",
    "MS-SAMPLE-10"
)

$actualChecks = @($payload.dashboards.checks | ForEach-Object { $_.checkId })
foreach ($checkId in $requiredChecks) {
    Assert-Condition ($checkId -in $actualChecks) "Acceptance evidence schema missing required check ID: $checkId"
}

foreach ($dashboard in $payload.dashboards) {
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($dashboard.acceptancePack)) "Dashboard evidence is missing acceptancePack"
    Assert-Condition (@($dashboard.checks).Count -gt 0) "Dashboard evidence has no checks: $($dashboard.dashboard)"
    foreach ($check in $dashboard.checks) {
        foreach ($property in @("dashboard", "checkId", "check", "source", "target", "passCriteria", "expectedEvidence", "result", "evidencePath", "reviewer", "notes")) {
            Assert-Condition ($property -in @($check.PSObject.Properties.Name)) "Check $($check.checkId) missing property: $property"
        }
    }
}

Write-Host "Acceptance evidence template validation: OK"
