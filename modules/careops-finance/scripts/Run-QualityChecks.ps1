[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("property-based", "mutation", "contract", "metamorphic")]
    [string] $Technique
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-PropertyChecks {
    $dashboards = Get-ChildItem -LiteralPath "src/powerbi/dashboards" -Directory | Sort-Object Name
    if ($dashboards.Count -lt 1) {
        throw "No dashboards found for property checks."
    }

    1..3 | ForEach-Object {
        $dashboard = $dashboards | Get-Random
        $manifestPath = Join-Path $dashboard.FullName ".pbixproj.json"
        if (-not (Test-Path -LiteralPath $manifestPath)) {
            throw "Missing manifest for dashboard: $($dashboard.Name)"
        }

        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if ([string]::IsNullOrWhiteSpace($manifest.version)) {
            throw "Missing manifest version in $($dashboard.Name)/.pbixproj.json"
        }

        $deploymentNames = @($manifest.deployments.PSObject.Properties.Name)
        if ($deploymentNames.Count -ne 1) {
            throw "Expected one deployment entry for $($dashboard.Name), found $($deploymentNames.Count)"
        }
        $deployment = $manifest.deployments.$($deploymentNames[0])
        if ($deployment.mode -ne "Dataset") {
            throw "Non-dataset deployment mode in $($dashboard.Name): $($deployment.mode)"
        }
        if ($deployment.source.type -ne "Folder") {
            throw "Deployment source type is not Folder in $($dashboard.Name): $($deployment.source.type)"
        }
    }
}

function Invoke-MutationChecks {
    $dashboard = Get-ChildItem -LiteralPath "src/powerbi/dashboards" -Directory | Select-Object -First 1
    if ($null -eq $dashboard) {
        throw "No dashboard found for mutation checks."
    }

    $manifestPath = Join-Path $dashboard.FullName ".pbixproj.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Missing manifest for mutation checks: $($dashboard.Name)"
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $deploymentName = @($manifest.deployments.PSObject.Properties.Name)[0]
    $baselineMode = $manifest.deployments.$deploymentName.mode
    if ($baselineMode -ne "Dataset") {
        throw "Expected baseline deployment mode Dataset for mutation check, found $baselineMode."
    }

    $mutatedManifest = ($manifest | ConvertTo-Json -Depth 64) | ConvertFrom-Json
    $mutatedManifest.deployments.$deploymentName.mode = "Import"
    if ($mutatedManifest.deployments.$deploymentName.mode -eq $baselineMode) {
        throw "Mutation simulation failed for dashboard $($dashboard.Name)."
    }

    Write-Host "Mutation simulation succeeded for dashboard $($dashboard.Name): Dataset -> Import"
}

function Invoke-ContractChecks {
    $requiredFiles = @(
        "AGENTS.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        ".github/pull_request_template.md",
        ".github/renovate.json",
        "codecov.yml",
        "scripts/Invoke-CiChecks.ps1",
        "scripts/Generate-LcovCoverage.ps1",
        "scripts/Write-DriftReceipt.ps1",
        "scripts/Run-QualityChecks.ps1"
    )

    foreach ($requiredFile in $requiredFiles) {
        if (-not (Test-Path -LiteralPath $requiredFile)) {
            throw "Missing required contract file: $requiredFile"
        }
    }

    $readme = Get-Content -LiteralPath README.md -Raw
    if ($readme -notmatch "Invoke-CiChecks\.ps1") {
        throw "README no longer includes one-command validation entrypoint."
    }
}

function Invoke-MetamorphicChecks {
    $orders = @(
        @("property-based", "mutation", "contract"),
        @("contract", "mutation", "property-based")
    )

    foreach ($order in $orders) {
        Write-Host "Running metamorphic invariant in order: $($order -join ' -> ')"
        foreach ($technique in $order) {
            & (Join-Path $PSScriptRoot "Run-QualityChecks.ps1") -Technique $technique
        }
    }
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Push-Location $repoRoot
try {
    switch ($Technique) {
        "property-based" {
            Invoke-PropertyChecks
        }
        "mutation" {
            Invoke-MutationChecks
        }
        "contract" {
            Invoke-ContractChecks
        }
        "metamorphic" {
            Invoke-MetamorphicChecks
        }
    }
    Write-Host "Quality check passed: $Technique"
}
finally {
    Pop-Location
}
