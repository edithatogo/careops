[CmdletBinding()]
param(
    [ValidateSet("all", "vmo-finance", "medical-staff")]
    [string] $Dashboard = "all",

    [string] $ConfigPath = "",

    [string] $OutRoot = "",

    [int] $CommandTimeoutSeconds = 120,

    [ValidateRange(0, [int]::MaxValue)]
    [int] $MaxRows = 1000
)

if ($PSVersionTable.PSEdition -ne "Desktop") {
    $forward = @()
    foreach ($entry in $PSBoundParameters.GetEnumerator()) {
        $forward += "-$($entry.Key)"
        if ($entry.Value -is [System.Management.Automation.SwitchParameter]) {
            if (-not $entry.Value.IsPresent) {
                $forward = $forward[0..($forward.Count - 2)]
            }
            continue
        }
        if ($entry.Value -is [array]) {
            $forward += @($entry.Value)
        }
        else {
            $forward += $entry.Value
        }
    }

    & "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath @forward
    exit $LASTEXITCODE
}

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = Join-Path $repoRoot "config\sources.json"
}
if ([string]::IsNullOrWhiteSpace($OutRoot)) {
    $OutRoot = Join-Path $repoRoot "data\extracts"
}

$configPathResolved = (Resolve-Path -LiteralPath $ConfigPath).Path
$config = Get-Content -LiteralPath $configPathResolved -Raw | ConvertFrom-Json
$exportScript = Join-Path $PSScriptRoot "Export-AccessTables.ps1"

$dashboardRegistry = @(
    [pscustomobject] @{
        id = "vmo-finance"
        displayName = "VMO Finance"
        sourceId = "vmo_reporting"
        outputFolder = "vmo-finance"
        tables = @(
            "tbl_Calendar",
            "tbl_GL_Transactions",
            "tbl_Reconciliation_GL_Data",
            "tbl_Reconciliation_VMO_Data",
            "tbl_VMO_Data",
            "tbl_VMO_GL_Classification",
            "tbl_VMO_GL_Transactions"
        )
    }
    [pscustomobject] @{
        id = "medical-staff"
        displayName = "Medical Staff"
        sourceId = "medical_staff_reporting"
        outputFolder = "medical-staff"
        tables = @(
            "tbl_Medical_Staff_Data",
            "tbl_Medical_Staff_History",
            "tbl_WF_Calendar"
        )
    }
)

$selectedDashboards = @(
    if ($Dashboard -eq "all") {
        $dashboardRegistry
    }
    else {
        $dashboardRegistry | Where-Object { $_.id -eq $Dashboard }
    }
)

if (@($selectedDashboards).Count -eq 0) {
    throw "Unknown dashboard '$Dashboard'."
}

foreach ($dashboardEntry in $selectedDashboards) {
    $source = @($config.sources | Where-Object { $_.id -eq $dashboardEntry.sourceId })
    if ($source.Count -ne 1) {
        throw "Expected one source with id '$($dashboardEntry.sourceId)' in '$configPathResolved'."
    }

    $databasePath = [string] $source[0].path
    if (-not [System.IO.Path]::IsPathRooted($databasePath)) {
        $databasePath = Join-Path $repoRoot $databasePath
    }
    $resolvedDatabasePath = (Resolve-Path -LiteralPath $databasePath).Path

    $dashboardOutDir = Join-Path $OutRoot $dashboardEntry.outputFolder
    New-Item -ItemType Directory -Force -Path $dashboardOutDir | Out-Null
    $resolvedOutDir = (Resolve-Path -LiteralPath $dashboardOutDir).Path

    $exportResults = & $exportScript `
        -DatabasePath $resolvedDatabasePath `
        -ObjectName $dashboardEntry.tables `
        -OutDir $resolvedOutDir `
        -CommandTimeoutSeconds $CommandTimeoutSeconds `
        -MaxRows $MaxRows

    foreach ($result in @($exportResults)) {
        [pscustomobject] [ordered] @{
            dashboard = $dashboardEntry.id
            dashboardDisplayName = $dashboardEntry.displayName
            database = [System.IO.Path]::GetFileName($resolvedDatabasePath)
            objectName = $result.ObjectName
            objectType = $result.ObjectType
            outputPath = $result.OutputPath
            rowCount = $result.RowCount
            maxRows = $MaxRows
        }
    }
}
