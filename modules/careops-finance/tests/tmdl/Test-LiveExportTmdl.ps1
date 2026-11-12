[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "../..")).Path

function Assert-Condition {
    param(
        [bool] $Condition,
        [string] $Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Get-CatalogueMeasureNames {
    param(
        [string] $CataloguePath
    )

    $measureNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $measurePattern = '^\|\s*`([^`]+)`\s*\|'
    foreach ($line in Get-Content -LiteralPath $CataloguePath) {
        $match = [regex]::Match($line, $measurePattern)
        if ($match.Success -and $match.Groups[1].Value -ne "Measure") {
            [void] $measureNames.Add($match.Groups[1].Value)
        }
    }

    return $measureNames
}

function Test-DashboardTmdlExport {
    param(
        [string] $DashboardName,
        [string[]] $RequiredTableFiles,
        [string[]] $RequiredExportedMeasureNames
    )

    $modelTmdlPath = Join-Path $repoRoot "src/powerbi/dashboards/$DashboardName/model-tmdl"
    $liveExportPath = Join-Path $modelTmdlPath "live-export"
    $tablesPath = Join-Path $liveExportPath "tables"
    $cataloguePath = Join-Path $modelTmdlPath "measure-catalogue.md"

    Assert-Condition (Test-Path -LiteralPath $liveExportPath -PathType Container) "Missing live TMDL export folder for $DashboardName"
    foreach ($requiredExportFile in @("database.tmdl", "model.tmdl")) {
        Assert-Condition (Test-Path -LiteralPath (Join-Path $liveExportPath $requiredExportFile) -PathType Leaf) "Missing live TMDL export file for ${DashboardName}: $requiredExportFile"
    }
    Assert-Condition (Test-Path -LiteralPath $tablesPath -PathType Container) "Missing live TMDL tables folder for $DashboardName"

    foreach ($requiredTableFile in $RequiredTableFiles) {
        Assert-Condition (Test-Path -LiteralPath (Join-Path $tablesPath $requiredTableFile) -PathType Leaf) "Missing live TMDL table file for ${DashboardName}: $requiredTableFile"
    }

    $catalogueMeasureNames = Get-CatalogueMeasureNames -CataloguePath $cataloguePath
    $tableTmdl = (Get-ChildItem -LiteralPath $tablesPath -Filter "*.tmdl" -File | ForEach-Object {
            Get-Content -LiteralPath $_.FullName -Raw
        }) -join [Environment]::NewLine

    foreach ($measureName in $RequiredExportedMeasureNames) {
        Assert-Condition ($catalogueMeasureNames.Contains($measureName)) "Required exported measure is not listed in ${DashboardName} measure catalogue: $measureName"
        $measurePattern = "(?m)^\s*measure\s+'$([regex]::Escape($measureName))'\s*="
        Assert-Condition ($tableTmdl -match $measurePattern) "Missing exported TMDL measure for ${DashboardName}: $measureName"
    }
}

$vmoRequiredTables = @(
    "VMO Calendar.tmdl",
    "VMO Data.tmdl",
    "VMO GL Bridge.tmdl",
    "VMO GL Classification.tmdl",
    "VMO GL Transactions.tmdl",
    "VMO Reconciliation GL.tmdl",
    "VMO Reconciliation VMO.tmdl"
)

$medicalRequiredTables = @(
    "Workforce Calendar.tmdl",
    "Medical Staff Data.tmdl",
    "Medical Staff History.tmdl"
)

Test-DashboardTmdlExport `
    -DashboardName "vmo-finance" `
    -RequiredTableFiles $vmoRequiredTables `
    -RequiredExportedMeasureNames @(
        "Total GL Amount",
        "Total VMO Amount",
        "GL Transaction Count",
        "VMO Record Count"
    )

Test-DashboardTmdlExport `
    -DashboardName "medical-staff" `
    -RequiredTableFiles $medicalRequiredTables `
    -RequiredExportedMeasureNames @(
        "Medical Staff Count",
        "Medical Staff FTE",
        "Medical Payroll Amount",
        "Payroll per Staff"
    )

Write-Host "Live TMDL export contract: OK"
