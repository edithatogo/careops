param(
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$requiredPaths = @(
    "pbip/DatixIncidentDashboard.pbip",
    "pbip/DatixIncidentDashboard.Report/definition.pbir",
    "pbip/DatixIncidentDashboard.Report/definition/report.json",
    "pbip/DatixIncidentDashboard.Report/definition/pages/pages.json",
    "pbip/DatixIncidentDashboard.SemanticModel/definition/model.tmdl",
    "pbip/DatixIncidentDashboard.SemanticModel/definition/relationships.tmdl",
    "pbip/DatixIncidentDashboard.SemanticModel/definition/tables/MeasureTable.tmdl",
    "pbip/DatixIncidentDashboard.SemanticModel/definition/tables/StandardsCoverage.tmdl",
    "pbip/DatixIncidentDashboard.Report/definition/pages/StandardsAlignment/page.json",
    "paginated_reports/prototype_manifest_v1_20260428.json",
    "scorecards/scorecard_manifest_v1_20260428.json"
)

$missing = @()
foreach ($relativePath in $requiredPaths) {
    $fullPath = Join-Path $RootPath $relativePath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        $missing += $relativePath
    }
}

$jsonPaths = @(
    "pbip/DatixIncidentDashboard.Report/definition.pbir",
    "pbip/DatixIncidentDashboard.Report/definition/pages/pages.json",
    "pbip/DatixIncidentDashboard.Report/definition/report.json",
    "paginated_reports/prototype_manifest_v1_20260428.json",
    "scorecards/scorecard_manifest_v1_20260428.json"
)

$jsonErrors = @()
foreach ($relativePath in $jsonPaths) {
    $fullPath = Join-Path $RootPath $relativePath
    try {
        Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json | Out-Null
    }
    catch {
        $jsonErrors += $relativePath
    }
}

$pageRoot = Join-Path $RootPath "pbip/DatixIncidentDashboard.Report/definition/pages"
$pageDirectories = @()
if (Test-Path -LiteralPath $pageRoot) {
    $pageDirectories = Get-ChildItem -LiteralPath $pageRoot -Directory | Select-Object -ExpandProperty Name
}

$pageTreeErrors = @()
$pagesManifestPath = Join-Path $RootPath "pbip/DatixIncidentDashboard.Report/definition/pages/pages.json"
if (Test-Path -LiteralPath $pagesManifestPath) {
    try {
        $pagesManifest = Get-Content -LiteralPath $pagesManifestPath -Raw | ConvertFrom-Json
        $manifestPageOrder = @($pagesManifest.pageOrder)

        foreach ($pageName in $manifestPageOrder) {
            $pagePath = Join-Path $pageRoot $pageName
            if (-not (Test-Path -LiteralPath $pagePath)) {
                $pageTreeErrors += "Missing page directory: $pageName"
                continue
            }

            $pageJsonPath = Join-Path $pagePath "page.json"
            if (-not (Test-Path -LiteralPath $pageJsonPath)) {
                $pageTreeErrors += "Missing page.json: $pageName"
                continue
            }

            try {
                Get-Content -LiteralPath $pageJsonPath -Raw | ConvertFrom-Json | Out-Null
            }
            catch {
                $pageTreeErrors += "Invalid page.json: $pageName"
            }

            $visualRoot = Join-Path $pagePath "visuals"
            if (Test-Path -LiteralPath $visualRoot) {
                foreach ($visualFile in Get-ChildItem -LiteralPath $visualRoot -Recurse -Filter visual.json -File) {
                    try {
                        Get-Content -LiteralPath $visualFile.FullName -Raw | ConvertFrom-Json | Out-Null
                    }
                    catch {
                        $pageTreeErrors += "Invalid visual.json: $($visualFile.FullName.Substring($RootPath.Length + 1))"
                    }
                }
            }
        }

        foreach ($pageDirectory in $pageDirectories) {
            if ($manifestPageOrder -notcontains $pageDirectory) {
                $pageTreeErrors += "Unlisted page directory: $pageDirectory"
            }
        }
    }
    catch {
        $pageTreeErrors += "Unable to parse pages manifest"
    }
}

$schemaIssues = @()
foreach ($schemaPath in @(
    "pbip/DatixIncidentDashboard.Report/definition.pbir",
    "pbip/DatixIncidentDashboard.Report/definition/pages/pages.json"
)) {
    $fullPath = Join-Path $RootPath $schemaPath
    if (-not (Test-Path -LiteralPath $fullPath)) {
        continue
    }

    try {
        $json = Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
        if ($json.PSObject.Properties.Name -contains '$schema') {
            $schemaValue = $json.'$schema'
            $schemaOk = $false
            if ($schemaPath -like '*definition.pbir') {
                $schemaOk = $schemaValue -match '^https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/(1|2)\.[0-9]+\.[0-9]+/schema\.json$'
            }
            elseif ($schemaPath -like '*pages.json') {
                $schemaOk = $schemaValue -match '^https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/(1|2)\.[0-9]+\.[0-9]+/schema\.json$'
            }
            if (-not $schemaOk) {
                $schemaIssues += "$schemaPath has unexpected $schema value: $schemaValue"
            }
        }
        else {
            $schemaIssues += "$schemaPath is missing $schema"
        }
    }
    catch {
        $schemaIssues += "$schemaPath could not be parsed for schema validation"
    }
}

$modelIssues = @()
$modelDefinitionRoot = Join-Path $RootPath "pbip/DatixIncidentDashboard.SemanticModel/definition"
$tablesRoot = Join-Path $modelDefinitionRoot "tables"
$modelPath = Join-Path $modelDefinitionRoot "model.tmdl"
$relationshipsPath = Join-Path $modelDefinitionRoot "relationships.tmdl"
$expressionsPath = Join-Path $modelDefinitionRoot "expressions.tmdl"

if (Test-Path -LiteralPath $tablesRoot) {
    foreach ($tableFile in Get-ChildItem -LiteralPath $tablesRoot -Filter "*.tmdl" -File) {
        $firstTableDeclaration = Select-String -LiteralPath $tableFile.FullName -Pattern '^\s*table\s+(.+?)\s*$' | Select-Object -First 1
        if ($firstTableDeclaration) {
            $declaredTableName = $firstTableDeclaration.Matches[0].Groups[1].Value.Trim("'")
            $expectedFileName = "$declaredTableName.tmdl"
            if ($tableFile.Name -cne $expectedFileName) {
                $modelIssues += "Table file '$($tableFile.Name)' declares table '$declaredTableName'; expected '$expectedFileName'."
            }
        }
    }
}

$loadedStagingTablePath = Join-Path $tablesRoot "Staging_IncidentsRaw.tmdl"
if (Test-Path -LiteralPath $loadedStagingTablePath) {
    $modelIssues += "Staging_IncidentsRaw must be a non-loaded expression, not an imported table."
}

if (Test-Path -LiteralPath $modelPath) {
    $modelText = Get-Content -LiteralPath $modelPath -Raw
    if ($modelText -match '(?m)^\s*ref table Staging_IncidentsRaw\s*$') {
        $modelIssues += "model.tmdl still references Staging_IncidentsRaw as a loaded table."
    }
}

if (Test-Path -LiteralPath $expressionsPath) {
    $expressionsText = Get-Content -LiteralPath $expressionsPath -Raw
    if ($expressionsText -notmatch '(?m)^\s*expression Staging_IncidentsRaw\s*=') {
        $modelIssues += "expressions.tmdl is missing the non-loaded Staging_IncidentsRaw expression."
    }
}

if (Test-Path -LiteralPath $relationshipsPath) {
    $relationshipsText = Get-Content -LiteralPath $relationshipsPath -Raw
    foreach ($requiredRelationship in @(
        "relationship DateToIncidentDate",
        "relationship OrganisationToIncidents",
        "relationship IncidentCategoryToIncidents",
        "relationship HarmToIncidents",
        "relationship DateToSurveillanceMonthly",
        "relationship DateToHealthConceptMonthly"
    )) {
        if ($relationshipsText -notmatch [regex]::Escape($requiredRelationship)) {
            $modelIssues += "Missing required relationship declaration: $requiredRelationship."
        }
    }
}

$nonAdditiveColumns = @{
    "FactIncidents.tmdl" = @("days_to_report", "incident_year", "incident_month", "incident_quarter")
    "DimDate.tmdl" = @("Year", "Quarter", "MonthNumber")
    "DimHarm.tmdl" = @("initial_harm_score", "confirmed_harm_score")
    "SurveillanceMonthly.tmdl" = @(
        "expected_count",
        "variance_count",
        "dispersion_index",
        "empirical_p95_limit",
        "empirical_p99_limit",
        "overdispersion_ucl_95",
        "overdispersion_ucl_99",
        "ewma_value",
        "ewma_ucl",
        "cusum_value",
        "run_above_median_length"
    )
    "HealthConceptQA.tmdl" = @("metric_value")
    "NarrativeTokens.tmdl" = @("token_count")
    "NarrativeKeyPhrases.tmdl" = @("phrase_word_count", "phrase_count")
    "NarrativeSentiment.tmdl" = @("positive_count", "negative_count", "sentiment_score")
    "NarrativeAnonymizationQA.tmdl" = @("long_digit_run_count")
    "ValidationTargets.tmdl" = @("target_value")
}

foreach ($entry in $nonAdditiveColumns.GetEnumerator()) {
    $tablePath = Join-Path $tablesRoot $entry.Key
    if (-not (Test-Path -LiteralPath $tablePath)) {
        continue
    }

    $tableText = Get-Content -LiteralPath $tablePath -Raw
    foreach ($columnName in $entry.Value) {
        $unsafePattern = "(?ms)^\s*column\s+$([regex]::Escape($columnName))\s+.*?^\s*summarizeBy:\s+sum\s*$"
        if ($tableText -match $unsafePattern) {
            $modelIssues += "$($entry.Key) column '$columnName' should not default to summarizeBy: sum."
        }
    }
}

$pbipPackage = Join-Path $RootPath "pbip/DatixIncidentDashboard.pbip"
$packageExists = Test-Path -LiteralPath $pbipPackage

[pscustomobject]@{
    RootPath = $RootPath
    PackageExists = $packageExists
    MissingRequiredPaths = $missing
    JsonParseFailures = $jsonErrors
    PageTreeIssues = $pageTreeErrors
    SchemaIssues = $schemaIssues
    ModelIssues = $modelIssues
    Status = if ($packageExists -and $missing.Count -eq 0 -and $jsonErrors.Count -eq 0 -and $pageTreeErrors.Count -eq 0 -and $schemaIssues.Count -eq 0 -and $modelIssues.Count -eq 0) { "Pass" } else { "Review" }
}
