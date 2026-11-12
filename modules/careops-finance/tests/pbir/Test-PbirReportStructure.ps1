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

function ConvertTo-SpecVisualType {
    param(
        [string] $Type
    )

    switch ($Type) {
        "barChart" { "bar" }
        "clusteredBarChart" { "bar" }
        "columnChart" { "column" }
        "lineChart" { "line" }
        "pivotTable" { "matrix" }
        "stacked_bar" { "bar" }
        "stackedBarChart" { "bar" }
        "tableEx" { "table" }
        default { $Type }
    }
}

function Get-ReportSpec {
    param(
        [string] $SpecPath
    )

    $pages = [ordered]@{}
    $currentPageId = $null

    foreach ($line in Get-Content -LiteralPath $SpecPath) {
        if ($line -match '^### .+ \(`(?<pageId>[^`]+)`\)') {
            $currentPageId = $Matches.pageId
            $pages[$currentPageId] = [ordered]@{}
            continue
        }

        if ($null -ne $currentPageId -and $line -match '^\| `(?<visualId>[^`]+)` \| (?<type>[^|]+) \| (?<position>[^|]+) \|') {
            $position = @($Matches.position.Split(",") | ForEach-Object { [int]$_.Trim() })
            Assert-Condition ($position.Count -eq 4) "Invalid visual position in spec ${SpecPath}: $line"

            $pages[$currentPageId][$Matches.visualId] = [pscustomobject]@{
                VisualId = $Matches.visualId
                Type = (ConvertTo-SpecVisualType -Type $Matches.type.Trim())
                X = $position[0]
                Y = $position[1]
                Width = $position[2]
                Height = $position[3]
            }
        }
    }

    Assert-Condition ($pages.Count -gt 0) "No pages were parsed from report spec: $SpecPath"
    return $pages
}

function Test-VisualAgainstSpec {
    param(
        [string] $DashboardName,
        [string] $PageId,
        [System.IO.DirectoryInfo] $VisualDirectory,
        [hashtable] $ExpectedVisuals
    )

    $visualPath = Join-Path $VisualDirectory.FullName "visual.json"
    Assert-Condition (Test-Path -LiteralPath $visualPath) "Missing visual.json for $DashboardName/$PageId/$($VisualDirectory.Name)"

    $visualJson = Get-Content -LiteralPath $visualPath -Raw | ConvertFrom-Json
    Assert-Condition ($visualJson.name -eq $VisualDirectory.Name) "Visual name does not match folder for $DashboardName/$PageId/$($VisualDirectory.Name)"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($visualJson.visual.visualType)) "Missing visual type for $DashboardName/$PageId/$($VisualDirectory.Name)"
    Assert-Condition ($null -ne $visualJson.position) "Missing visual position for $DashboardName/$PageId/$($VisualDirectory.Name)"

    foreach ($propertyName in @("x", "y", "width", "height")) {
        Assert-Condition ($null -ne $visualJson.position.$propertyName) "Missing position.$propertyName for $DashboardName/$PageId/$($VisualDirectory.Name)"
    }

    if (-not $ExpectedVisuals.Contains($VisualDirectory.Name)) {
        return
    }

    $expected = $ExpectedVisuals[$VisualDirectory.Name]
    $actualType = ConvertTo-SpecVisualType -Type $visualJson.visual.visualType
    Assert-Condition ($actualType -eq $expected.Type) "Visual type mismatch for $DashboardName/$PageId/$($VisualDirectory.Name): expected $($expected.Type), got $actualType"
    Assert-Condition ([int]$visualJson.position.x -eq $expected.X) "Visual x mismatch for $DashboardName/$PageId/$($VisualDirectory.Name)"
    Assert-Condition ([int]$visualJson.position.y -eq $expected.Y) "Visual y mismatch for $DashboardName/$PageId/$($VisualDirectory.Name)"
    Assert-Condition ([int]$visualJson.position.width -eq $expected.Width) "Visual width mismatch for $DashboardName/$PageId/$($VisualDirectory.Name)"
    Assert-Condition ([int]$visualJson.position.height -eq $expected.Height) "Visual height mismatch for $DashboardName/$PageId/$($VisualDirectory.Name)"
}

function Get-VisualCoverageSummary {
    param(
        [string] $DashboardName,
        [string] $PageId,
        [string[]] $ExpectedVisualIds,
        [string[]] $GeneratedVisualIds
    )

    $missingVisualIds = @($ExpectedVisualIds | Where-Object { $GeneratedVisualIds -notcontains $_ })
    $extraVisualIds = @($GeneratedVisualIds | Where-Object { $ExpectedVisualIds -notcontains $_ })

    return [pscustomobject]@{
        DashboardName = $DashboardName
        PageId = $PageId
        ExpectedVisualIds = @($ExpectedVisualIds)
        GeneratedVisualIds = @($GeneratedVisualIds)
        MissingVisualIds = $missingVisualIds
        ExtraVisualIds = $extraVisualIds
    }
}

function Test-PbirReportStructure {
    param(
        [string] $DashboardName,
        [string] $SpecRelativePath,
        [string] $ReportRelativePath
    )

    $specPath = Join-Path $repoRoot $SpecRelativePath
    $reportPath = Join-Path $repoRoot $ReportRelativePath
    $definitionPath = Join-Path $reportPath "definition"
    $pagesPath = Join-Path $definitionPath "pages"
    $pagesMetadataPath = Join-Path $pagesPath "pages.json"
    $pageCoverage = [System.Collections.Generic.List[object]]::new()
    $coverageIssues = $false

    Assert-Condition (Test-Path -LiteralPath $specPath) "Missing report implementation spec for ${DashboardName}: $SpecRelativePath"
    Assert-Condition (Test-Path -LiteralPath $reportPath) "Missing PBIR report folder for ${DashboardName}: $ReportRelativePath"
    Assert-Condition (Test-Path -LiteralPath (Join-Path $reportPath "definition.pbir")) "Missing definition.pbir for $DashboardName"
    Assert-Condition (Test-Path -LiteralPath (Join-Path $definitionPath "report.json")) "Missing definition/report.json for $DashboardName"
    Assert-Condition (Test-Path -LiteralPath (Join-Path $definitionPath "version.json")) "Missing definition/version.json for $DashboardName"
    Assert-Condition (Test-Path -LiteralPath $pagesMetadataPath) "Missing definition/pages/pages.json for $DashboardName"

    $specPages = Get-ReportSpec -SpecPath $specPath
    $pagesMetadata = Get-Content -LiteralPath $pagesMetadataPath -Raw | ConvertFrom-Json
    $pageOrder = @($pagesMetadata.pageOrder)

    $expectedPageIds = @($specPages.Keys)
    $generatedExpectedPageIds = @($pageOrder | Where-Object { $specPages.Contains($_) })
    $expectedGeneratedPageIds = @($expectedPageIds | Where-Object { $pageOrder -contains $_ })
    Assert-Condition (($generatedExpectedPageIds -join "`n") -eq ($expectedGeneratedPageIds -join "`n")) "Page order mismatch for ${DashboardName}: expected generated page order $($expectedGeneratedPageIds -join ', '), got $($generatedExpectedPageIds -join ', ')"

    $missingPageIds = @($expectedPageIds | Where-Object { $pageOrder -notcontains $_ })
    $extraPageIds = @($pageOrder | Where-Object { $expectedPageIds -notcontains $_ })

    foreach ($pageId in $pageOrder) {
        $pagePath = Join-Path $pagesPath $pageId
        $pageJsonPath = Join-Path $pagePath "page.json"
        Assert-Condition (Test-Path -LiteralPath $pageJsonPath) "Missing page.json for $DashboardName/$pageId"

        $pageJson = Get-Content -LiteralPath $pageJsonPath -Raw | ConvertFrom-Json
        Assert-Condition ($pageJson.name -eq $pageId) "Page name mismatch for $DashboardName/$pageId"
        Assert-Condition ([int]$pageJson.width -eq 1280) "Page width mismatch for $DashboardName/$pageId"
        Assert-Condition ([int]$pageJson.height -eq 720) "Page height mismatch for $DashboardName/$pageId"

        $visualDirectories = @(Get-ChildItem -LiteralPath (Join-Path $pagePath "visuals") -Directory -ErrorAction SilentlyContinue)
        $generatedVisualIds = @($visualDirectories.Name)
        $expectedVisualIds = @()
        if ($specPages.Contains($pageId)) {
            $expectedVisualIds = @($specPages[$pageId].Keys)
        }

        $pageCoverage.Add((Get-VisualCoverageSummary -DashboardName $DashboardName -PageId $pageId -ExpectedVisualIds $expectedVisualIds -GeneratedVisualIds $generatedVisualIds))

        foreach ($visualDirectory in $visualDirectories) {
            if ($specPages.Contains($pageId) -and $specPages[$pageId].Contains($visualDirectory.Name)) {
                Test-VisualAgainstSpec -DashboardName $DashboardName -PageId $pageId -VisualDirectory $visualDirectory -ExpectedVisuals $specPages[$pageId]
                continue
            }

            $visualPath = Join-Path $visualDirectory.FullName "visual.json"
            Assert-Condition (Test-Path -LiteralPath $visualPath) "Missing visual.json for $DashboardName/$pageId/$($visualDirectory.Name)"

            $visualJson = Get-Content -LiteralPath $visualPath -Raw | ConvertFrom-Json
            Assert-Condition ($visualJson.name -eq $visualDirectory.Name) "Visual name does not match folder for $DashboardName/$pageId/$($VisualDirectory.Name)"
            Assert-Condition (-not [string]::IsNullOrWhiteSpace($visualJson.visual.visualType)) "Missing visual type for $DashboardName/$PageId/$($VisualDirectory.Name)"
            Assert-Condition ($null -ne $visualJson.position) "Missing visual position for $DashboardName/$PageId/$($VisualDirectory.Name)"

            foreach ($propertyName in @("x", "y", "width", "height")) {
                Assert-Condition ($null -ne $visualJson.position.$propertyName) "Missing position.$propertyName for $DashboardName/$PageId/$($VisualDirectory.Name)"
            }
        }

        $coverageProblems = @($pageCoverage | Where-Object { $_.MissingVisualIds.Count -gt 0 -or $_.ExtraVisualIds.Count -gt 0 })
        if ($coverageProblems.Count -gt 0) {
            $coverageIssues = $true
        }
    }

    foreach ($missingPageId in $missingPageIds) {
        $pageCoverage.Add([pscustomobject]@{
            DashboardName = $DashboardName
            PageId = $missingPageId
            ExpectedVisualIds = @($specPages[$missingPageId].Keys)
            GeneratedVisualIds = @()
            MissingVisualIds = @($specPages[$missingPageId].Keys)
            ExtraVisualIds = @()
        })
    }

    if ($coverageIssues -or $missingPageIds.Count -gt 0 -or $extraPageIds.Count -gt 0) {
        Write-Warning ("PBIR coverage summary for {0}: {1}" -f $DashboardName, ([pscustomobject]@{
            DashboardName = $DashboardName
            MissingPageIds = @($missingPageIds)
            ExtraPageIds = @($extraPageIds)
            PageCoverage = @($pageCoverage)
        } | ConvertTo-Json -Depth 8 -Compress))
    }

    Write-Host "PBIR report structure: OK ($DashboardName)"
}

$dashboards = @(
    @{
        Name = "VMO Finance"
        Spec = "src/powerbi/dashboards/vmo-finance/report/report-implementation-spec.md"
        Report = "src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance/VMO Finance.Report"
    },
    @{
        Name = "Medical Staff"
        Spec = "src/powerbi/dashboards/medical-staff/report/report-implementation-spec.md"
        Report = "src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff/Medical Staff.Report"
    }
)

foreach ($dashboard in $dashboards) {
    Test-PbirReportStructure -DashboardName $dashboard.Name -SpecRelativePath $dashboard.Spec -ReportRelativePath $dashboard.Report
}
