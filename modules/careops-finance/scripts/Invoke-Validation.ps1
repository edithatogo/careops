[CmdletBinding()]
param(
    [ValidateSet("RepositoryHygiene", "SourceControlReady", "PublishRefreshReady")]
    [string] $Mode = "RepositoryHygiene",
    [switch] $SkipPowerBiCli,
    [switch] $RequirePowerBiExports
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

if ($RequirePowerBiExports -and $Mode -eq "RepositoryHygiene") {
    $Mode = "SourceControlReady"
}

function Assert-Condition {
    param(
        [bool] $Condition,
        [string] $Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Test-GitIgnoredPath {
    param(
        [string] $Path,
        [string] $Message
    )

    git check-ignore -q -- $Path
    Assert-Condition ($LASTEXITCODE -eq 0) $Message
}

function Test-RequiredFile {
    param(
        [string] $RelativePath,
        [string] $Message
    )

    Assert-Condition (Test-Path -LiteralPath (Join-Path $repoRoot $RelativePath)) $Message
}

function Test-FileContainsAll {
    param(
        [string] $RelativePath,
        [string[]] $Patterns,
        [string] $MessagePrefix
    )

    $content = Get-Content -LiteralPath (Join-Path $repoRoot $RelativePath) -Raw
    foreach ($pattern in $Patterns) {
        Assert-Condition ($content -match [regex]::Escape($pattern)) "$MessagePrefix missing required text: $pattern"
    }
}

function Test-NoTrackedForbiddenFiles {
    param(
        [string[]] $PathSpecs
    )

    $tracked = & git ls-files -- $PathSpecs
    Assert-Condition (@($tracked).Count -eq 0) ("Tracked forbidden files found:`n" + (@($tracked) -join [Environment]::NewLine))
}

function Test-PowerBiDashboardManifest {
    param(
        [string] $DashboardName,
        [string] $DashboardPath,
        [string] $SourceDatabasePath
    )

    $requiredItems = @(
        "README.md",
        ".pbixproj.json",
        "Dataset",
        "m",
        "model-tmdl",
        "report"
    )

    foreach ($item in $requiredItems) {
        Assert-Condition (Test-Path -LiteralPath (Join-Path $DashboardPath $item)) "Missing required Power BI dashboard item: $DashboardName/$item"
    }

    $manifestPath = Join-Path $DashboardPath ".pbixproj.json"
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    Assert-Condition ($null -ne $manifest.version) "Missing version in $DashboardName/.pbixproj.json"

    $deploymentNames = @($manifest.deployments.PSObject.Properties.Name)
    Assert-Condition ($deploymentNames.Count -eq 1) "Expected one deployment profile in $DashboardName/.pbixproj.json"

    $deploymentName = $deploymentNames[0]
    $deployment = $manifest.deployments.$deploymentName

    Assert-Condition (-not [string]::IsNullOrWhiteSpace($deployment.description)) "Missing deployment description in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.mode -eq "Dataset") "Deployment mode must be Dataset in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.source.type -eq "Folder") "Deployment source type must be Folder in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.source.path -eq "./Dataset") "Deployment source path must be ./Dataset in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.authentication.type -eq "ServicePrincipal") "Deployment authentication must use ServicePrincipal in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.authentication.validateAuthority -eq $true) "Deployment authority validation must stay enabled in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.authentication.tenantId -eq "%PBI_TENANT_ID%") "Deployment tenant placeholder must stay environment-based in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.authentication.clientId -eq "%PBI_CLIENT_ID%") "Deployment client placeholder must stay environment-based in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.authentication.clientSecret -eq "%PBI_CLIENT_SECRET%") "Deployment secret placeholder must stay environment-based in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.options.refresh.enabled -eq $false) "Deployment refresh must remain disabled in $DashboardName/.pbixproj.json"
    Assert-Condition ($deployment.parameters.AccessDatabasePath -eq $SourceDatabasePath) "Deployment AccessDatabasePath must point at $SourceDatabasePath in $DashboardName/.pbixproj.json"

    foreach ($environmentName in @("Development", "Production")) {
        $environment = $deployment.environments.$environmentName
        Assert-Condition ($null -ne $environment) "Missing $environmentName environment in $DashboardName/.pbixproj.json"
        Assert-Condition ($environment.disabled -eq $true) "Environment $environmentName must remain disabled in $DashboardName/.pbixproj.json"
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($environment.workspace)) "Environment $environmentName must have a placeholder workspace in $DashboardName/.pbixproj.json"
    }
}

function Get-PowerBiDashboardExportState {
    param(
        [string] $DashboardName,
        [string] $DashboardPath
    )

    $modelTmdlPath = Join-Path $DashboardPath "model-tmdl"
    $reportPath = Join-Path $DashboardPath "report"
    $tmdlFiles = @(Get-ChildItem -LiteralPath $modelTmdlPath -Filter "*.tmdl" -File -Recurse -ErrorAction SilentlyContinue)
    $reportExports = @(Get-ChildItem -LiteralPath $reportPath -Filter "*.Report" -Directory -Recurse -ErrorAction SilentlyContinue)
    $datasetFiles = @(Get-ChildItem -LiteralPath (Join-Path $DashboardPath "Dataset") -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" })

    [pscustomobject]@{
        DashboardName = $DashboardName
        ModelTmdlPath = $modelTmdlPath
        HasTmdlExport = ($tmdlFiles.Count -gt 0)
        ReportExports = $reportExports
        HasReportExport = ($reportExports.Count -gt 0)
        HasDatasetSource = ($datasetFiles.Count -gt 0)
    }
}

function Test-RequiredEnvironmentVariable {
    param(
        [string] $Name
    )

    $value = [Environment]::GetEnvironmentVariable($Name)
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($value)) "Publish refresh readiness requires environment variable $Name"
}

function Test-PowerBiReportExport {
    param(
        [System.IO.DirectoryInfo] $ReportExport
    )

    $requiredFiles = @(
        "definition.pbir",
        "definition/version.json",
        "definition/report.json",
        "definition/pages/pages.json"
    )

    foreach ($requiredFile in $requiredFiles) {
        Assert-Condition (Test-Path -LiteralPath (Join-Path $ReportExport.FullName $requiredFile)) "Missing PBIR export file: $($ReportExport.FullName)/$requiredFile"
    }

    $jsonFiles = @(Get-ChildItem -LiteralPath $ReportExport.FullName -Filter "*.json" -File -Recurse)
    foreach ($jsonFile in $jsonFiles) {
        try {
            Get-Content -LiteralPath $jsonFile.FullName -Raw | ConvertFrom-Json | Out-Null
        }
        catch {
            throw "Invalid JSON in PBIR export file: $($jsonFile.FullName)"
        }
    }

    $staleBindingPattern = "FactMedical|DimWorkforce|FactMedicalPayroll|Source Inventory|Validation Checks|tbl_GL_Transactions|tbl_VMO_Data|tbl_Calendar|tbl_Reconciliation|tbl_VMO_GL|qry_Reconciliation"
    foreach ($jsonFile in $jsonFiles) {
        $jsonContent = Get-Content -LiteralPath $jsonFile.FullName -Raw
        Assert-Condition ($jsonContent -notmatch $staleBindingPattern) "PBIR export still contains SQL-contract-only visual bindings in local proof package: $($jsonFile.FullName)"
    }

    $definitionPbirPath = Join-Path $ReportExport.FullName "definition.pbir"
    $definitionPbir = Get-Content -LiteralPath $definitionPbirPath -Raw | ConvertFrom-Json
    if ($null -ne $definitionPbir.datasetReference.byPath.path) {
        $datasetPath = Join-Path $ReportExport.FullName $definitionPbir.datasetReference.byPath.path
        $datasetPath = (Resolve-Path -LiteralPath $datasetPath -ErrorAction SilentlyContinue).Path
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($datasetPath)) "PBIR datasetReference path does not resolve for $($ReportExport.FullName): $($definitionPbir.datasetReference.byPath.path)"
        Assert-Condition (Test-Path -LiteralPath (Join-Path $datasetPath "definition.pbism") -PathType Leaf) "Missing semantic model definition.pbism for PBIR datasetReference: $datasetPath"
        Assert-Condition (Test-Path -LiteralPath (Join-Path $datasetPath "definition") -PathType Container) "Missing semantic model TMDL definition folder for PBIR datasetReference: $datasetPath"
    }
}

function Test-EmbeddedSampleData {
    param(
        [System.IO.DirectoryInfo] $DashboardPath
    )

    $sampleScript = Join-Path $repoRoot "scripts/Set-PbirEmbeddedSampleData.ps1"
    Assert-Condition (Test-Path -LiteralPath $sampleScript -PathType Leaf) "Missing embedded sample data script: scripts/Set-PbirEmbeddedSampleData.ps1"

    $datasetTableRoots = @(Get-ChildItem -LiteralPath $DashboardPath.FullName -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object {
        ($_.FullName -replace "\\", "/") -like "*/report/pbir/*/Dataset/definition/tables"
    })

    Assert-Condition ($datasetTableRoots.Count -gt 0) "Missing PBIP Dataset table root for embedded sample validation: $($DashboardPath.FullName)"

    foreach ($tableRoot in $datasetTableRoots) {
        $tableFiles = @(Get-ChildItem -LiteralPath $tableRoot.FullName -Filter "*.tmdl" -File)
        Assert-Condition ($tableFiles.Count -gt 0) "No TMDL table files found for embedded sample validation: $($tableRoot.FullName)"
        foreach ($tableFile in $tableFiles) {
            $content = Get-Content -LiteralPath $tableFile.FullName -Raw
            Assert-Condition ($content -notmatch "Access\.Database|File\.Contents\(") "Local PBIP sample dataset still depends on Access files: $($tableFile.FullName)"
            Assert-Condition ($content -match "Table\.FromRecords") "Local PBIP sample dataset table is not embedded: $($tableFile.FullName)"
        }
    }
}

function Test-PowerBiExportReadiness {
    param(
        [pscustomobject] $ExportState,
        [string] $ValidationMode
    )

    if ($ValidationMode -in @("SourceControlReady", "PublishRefreshReady")) {
        Assert-Condition $ExportState.HasTmdlExport "Missing live TMDL export for $($ExportState.DashboardName): $($ExportState.ModelTmdlPath)"
        Assert-Condition $ExportState.HasReportExport "Missing live PBIR report export for $($ExportState.DashboardName): report/*.Report"
    }

    if ($ValidationMode -eq "PublishRefreshReady") {
        Assert-Condition $ExportState.HasDatasetSource "Missing pbi-tools Dataset source files for $($ExportState.DashboardName): Dataset/"
    }

    if ($ExportState.HasTmdlExport) {
        $tmdlReadme = Join-Path $ExportState.ModelTmdlPath "README.md"
        if (Test-Path -LiteralPath $tmdlReadme) {
            $readme = Get-Content -LiteralPath $tmdlReadme -Raw
            Assert-Condition ($readme -notmatch "No exported TMDL exists yet|reserved for a future|placeholder") "TMDL README still describes a placeholder after live TMDL export for $($ExportState.DashboardName)"
        }
    }

    foreach ($reportExport in $ExportState.ReportExports) {
        Test-PowerBiReportExport -ReportExport $reportExport
    }
}

function Test-PublishRefreshReadiness {
    foreach ($environmentVariable in @(
        "PBI_SQL_SERVER_HOST",
        "PBI_SQL_DATABASE",
        "PBI_GATEWAY_ID",
        "PBI_TENANT_ID",
        "PBI_CLIENT_ID",
        "PBI_CLIENT_SECRET"
    )) {
        Test-RequiredEnvironmentVariable -Name $environmentVariable
    }
}

Push-Location $repoRoot
try {
    Write-Host "Validation mode: $Mode"

    $scripts = Get-ChildItem -LiteralPath "scripts" -Filter "*.ps1"
    foreach ($script in $scripts) {
        $tokens = $null
        $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($script.FullName, [ref] $tokens, [ref] $errors) | Out-Null
        if ($errors.Count -gt 0) {
            $message = ($errors | ForEach-Object { "$($script.Name): $($_.Message)" }) -join [Environment]::NewLine
            throw $message
        }
    }
    $testScripts = @(Get-ChildItem -LiteralPath "tests" -Filter "*.ps1" -File -Recurse -ErrorAction SilentlyContinue)
    foreach ($testScript in $testScripts) {
        $tokens = $null
        $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($testScript.FullName, [ref] $tokens, [ref] $errors) | Out-Null
        if ($errors.Count -gt 0) {
            $message = ($errors | ForEach-Object { "$($testScript.Name): $($_.Message)" }) -join [Environment]::NewLine
            throw $message
        }
    }
    Write-Host "PowerShell syntax: OK"

    if ($Mode -eq "PublishRefreshReady") {
        Test-PublishRefreshReadiness
        Write-Host "Publish refresh environment: OK"
    }

    if ($Mode -in @("SourceControlReady", "PublishRefreshReady")) {
        $dsnContractTest = Join-Path $repoRoot "tests/dsn/Test-OdbcDsnSourceContract.ps1"
        Assert-Condition (Test-Path -LiteralPath $dsnContractTest) "Missing DSN source contract test: tests/dsn/Test-OdbcDsnSourceContract.ps1"
        & $dsnContractTest

        $acceptanceEvidenceTest = Join-Path $repoRoot "tests/acceptance/Test-AcceptanceEvidenceTemplate.ps1"
        Assert-Condition (Test-Path -LiteralPath $acceptanceEvidenceTest) "Missing acceptance evidence template test: tests/acceptance/Test-AcceptanceEvidenceTemplate.ps1"
        & $acceptanceEvidenceTest

        $pbirStructureTest = Join-Path $repoRoot "tests/pbir/Test-PbirReportStructure.ps1"
        Assert-Condition (Test-Path -LiteralPath $pbirStructureTest) "Missing PBIR report structure test: tests/pbir/Test-PbirReportStructure.ps1"
        & $pbirStructureTest

        $tmdlContractTest = Join-Path $repoRoot "tests/tmdl/Test-LiveExportTmdl.ps1"
        Assert-Condition (Test-Path -LiteralPath $tmdlContractTest) "Missing live TMDL export contract test: tests/tmdl/Test-LiveExportTmdl.ps1"
        & $tmdlContractTest

        $syntheticFinanceSliceTest = Join-Path $repoRoot "tests/finance/Test-SyntheticVmoPeriodSlice.ps1"
        Assert-Condition (Test-Path -LiteralPath $syntheticFinanceSliceTest) "Missing synthetic finance period slice test: tests/finance/Test-SyntheticVmoPeriodSlice.ps1"
        & $syntheticFinanceSliceTest
    }

    Test-RequiredFile -RelativePath "docs/dashboard-acceptance.md" -Message "Missing required readiness document: docs/dashboard-acceptance.md"
    Test-RequiredFile -RelativePath "docs/powerbi-alm.md" -Message "Missing required readiness document: docs/powerbi-alm.md"
    Test-FileContainsAll -RelativePath "docs/dashboard-acceptance.md" -Patterns @(
        "VMO Finance Acceptance Checklist"
        "Medical Staff Acceptance Checklist"
        "Readiness Modes"
        "Validation Notes Template"
        "Publish Blocker Register"
    ) -MessagePrefix "docs/dashboard-acceptance.md"
    Test-FileContainsAll -RelativePath "docs/powerbi-alm.md" -Patterns @(
        "Dry-Run ALM"
        "Validation Modes"
        "docs/dashboard-acceptance.md"
        "Keep deployment profiles disabled"
    ) -MessagePrefix "docs/powerbi-alm.md"

    $srcPowerBiRoot = Join-Path $repoRoot "src/powerbi"
    foreach ($requiredFolder in @("dashboards", "shared", "Deployment")) {
        Assert-Condition (Test-Path -LiteralPath (Join-Path $srcPowerBiRoot $requiredFolder)) "Missing required Power BI source folder: src/powerbi/$requiredFolder"
    }

    $dashboardRoot = Join-Path $srcPowerBiRoot "dashboards"
    $dashboardDirectories = Get-ChildItem -LiteralPath $dashboardRoot -Directory
    Assert-Condition ($dashboardDirectories.Count -gt 0) "No Power BI dashboard folders were found under src/powerbi/dashboards"

    foreach ($dashboard in $dashboardDirectories) {
        $sourceDatabasePath = switch ($dashboard.Name) {
            "vmo-finance" { "data/raw/VMO Reporting.accdb" }
            "medical-staff" { "data/raw/Medical_Staff_Reporting.accdb" }
            default { throw "Unexpected dashboard folder: $($dashboard.Name)" }
        }

        Test-PowerBiDashboardManifest -DashboardName $dashboard.Name -DashboardPath $dashboard.FullName -SourceDatabasePath $sourceDatabasePath
        $exportState = Get-PowerBiDashboardExportState -DashboardName $dashboard.Name -DashboardPath $dashboard.FullName
        Test-PowerBiExportReadiness -ExportState $exportState -ValidationMode $Mode
        Test-EmbeddedSampleData -DashboardPath $dashboard
    }
    Write-Host "Power BI dashboard layout: OK"

    $ignoredProbes = @(
        "data/raw/.gitignore-probe.accdb",
        "data/raw/.gitignore-probe.laccdb",
        "data/profile/.gitignore-probe.json",
        "data/extracts/.gitignore-probe.csv"
    )

    foreach ($ignoredProbe in $ignoredProbes) {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent (Join-Path $repoRoot $ignoredProbe)) | Out-Null
        Set-Content -LiteralPath (Join-Path $repoRoot $ignoredProbe) -Value "probe" -Encoding ASCII
    }
    try {
        foreach ($ignoredProbe in $ignoredProbes) {
            Test-GitIgnoredPath -Path $ignoredProbe -Message "Git ignore check failed for $ignoredProbe"
        }
    }
    finally {
        foreach ($ignoredProbe in $ignoredProbes) {
            Remove-Item -LiteralPath (Join-Path $repoRoot $ignoredProbe) -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "Git data ignore: OK"

    Test-NoTrackedForbiddenFiles -PathSpecs @(
        "*.accdb"
        "*.laccdb"
        "*.pbix"
        "*.pbit"
        "*.pbip.bak"
        ".env"
        "data/raw"
        "data/extracts"
        "data/profile"
    )
    Write-Host "Tracked source-control hygiene: OK"

    if (-not $SkipPowerBiCli) {
        pbi --help | Out-Null
        pbi report --help | Out-Null
        pbi database --help | Out-Null
        pbi-tools info | Out-Null
        Write-Host "Power BI CLI tools: OK"
    }

    Write-Host "Validation complete."
}
finally {
    Pop-Location
}
