[CmdletBinding()]
param(
    [ValidateSet("Both", "VmoFinance", "MedicalStaff")]
    [string] $Dashboard = "Both",

    [ValidateSet("Markdown", "Json")]
    [string] $Format = "Markdown",

    [string] $OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

function ConvertFrom-MarkdownTableRow {
    param([string] $Line)

    return @(($Line.Trim().Trim("|") -split "\|") | ForEach-Object { $_.Trim() })
}

function ConvertTo-MarkdownCell {
    param([AllowNull()][object] $Value)

    if ($null -eq $Value) {
        return ""
    }

    return ([string] $Value).Replace("|", "\|").Replace("`r", " ").Replace("`n", " ")
}

function ConvertTo-CamelPropertyName {
    param([string] $Value)

    $normalized = ([string] $Value) -replace '[^A-Za-z0-9]+', ' '
    $words = @(($normalized.Trim() -split '\s+') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($words.Count -eq 0) {
        return ""
    }

    $name = $words[0].Substring(0, 1).ToLowerInvariant() + $words[0].Substring(1)
    for ($i = 1; $i -lt $words.Count; $i++) {
        $name += $words[$i].Substring(0, 1).ToUpperInvariant() + $words[$i].Substring(1)
    }

    return $name
}

function Get-OrderedValue {
    param(
        [System.Collections.Specialized.OrderedDictionary] $Row,
        [string[]] $Keys
    )

    foreach ($key in $Keys) {
        if ($Row.Contains($key)) {
            return $Row[$key]
        }
    }

    return ""
}

function Get-MarkdownTables {
    param([string] $Path)

    $lines = Get-Content -LiteralPath $Path
    $tables = New-Object System.Collections.Generic.List[object]
    $current = New-Object System.Collections.Generic.List[string]

    foreach ($line in $lines) {
        if ($line -match '^\s*\|') {
            $current.Add($line)
            continue
        }

        if ($current.Count -gt 0) {
            $tables.Add($current.ToArray())
            $current = New-Object System.Collections.Generic.List[string]
        }
    }

    if ($current.Count -gt 0) {
        $tables.Add($current.ToArray())
    }

    return $tables.ToArray()
}

function ConvertFrom-AcceptancePackChecks {
    param(
        [string] $DashboardName,
        [string] $PackPath,
        [string] $CheckIdPattern
    )

    $checks = New-Object System.Collections.Generic.List[object]
    $seenCheckIds = New-Object System.Collections.Generic.HashSet[string]
    foreach ($table in Get-MarkdownTables -Path $PackPath) {
        if ($table.Count -lt 3) {
            continue
        }

        $headers = ConvertFrom-MarkdownTableRow -Line $table[0]
        $idColumn = [Array]::IndexOf($headers, "Check ID")
        if ($idColumn -lt 0) {
            $idColumn = [Array]::IndexOf($headers, "ID")
        }
        if ($idColumn -lt 0) {
            continue
        }

        for ($i = 2; $i -lt $table.Count; $i++) {
            $cells = ConvertFrom-MarkdownTableRow -Line $table[$i]
            if ($cells.Count -le $idColumn) {
                continue
            }

            $checkId = $cells[$idColumn].Trim([char] 0x60).Trim()
            if ($checkId -notmatch $CheckIdPattern) {
                continue
            }
            if (-not $seenCheckIds.Add($checkId)) {
                continue
            }

            $row = [ordered] @{}
            for ($columnIndex = 0; $columnIndex -lt $headers.Count; $columnIndex++) {
                $key = ConvertTo-CamelPropertyName -Value $headers[$columnIndex]
                if ([string]::IsNullOrWhiteSpace($key)) {
                    continue
                }

                $value = if ($columnIndex -lt $cells.Count) { $cells[$columnIndex] } else { "" }
                $row[$key] = $value
            }

            $checkText = Get-OrderedValue -Row $row -Keys @("check", "checkToPerform")
            $sourceText = Get-OrderedValue -Row $row -Keys @("accessSideSource", "sourceObject")
            $targetText = Get-OrderedValue -Row $row -Keys @("powerBIResult", "modelReportTarget")
            $passCriteriaText = Get-OrderedValue -Row $row -Keys @("passCriteria", "acceptanceResult")
            $expectedEvidenceText = Get-OrderedValue -Row $row -Keys @("evidence")

            $checks.Add([pscustomobject] [ordered] @{
                dashboard = $DashboardName
                checkId = $checkId
                check = $checkText
                source = $sourceText
                target = $targetText
                passCriteria = $passCriteriaText
                expectedEvidence = $expectedEvidenceText
                result = "Pending"
                evidencePath = ""
                reviewer = ""
                notes = ""
            })
        }
    }

    return $checks.ToArray()
}

function New-DashboardAcceptanceEvidence {
    param(
        [string] $DashboardName,
        [string] $AcceptancePackPath,
        [string] $CheckIdPattern
    )

    return [pscustomobject] [ordered] @{
        dashboard = $DashboardName
        acceptancePack = ($AcceptancePackPath.Substring($repoRoot.Length + 1) -replace "\\", "/")
        generatedAt = (Get-Date).ToString("o")
        boundary = "Template scaffold only. Fill with reviewer evidence from Access/sample outputs and source-controlled report/model evidence. Does not require SQL host, gateway, live Power BI, or source mutation."
        checks = @(ConvertFrom-AcceptancePackChecks -DashboardName $DashboardName -PackPath $AcceptancePackPath -CheckIdPattern $CheckIdPattern)
        sqlHostOpenItems = @(
            "SQL Server host/database/schema",
            "Credential mode",
            "Gateway binding",
            "Published refresh evidence"
        )
    }
}

function ConvertTo-AcceptanceMarkdown {
    param([object[]] $Evidence)

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# Dashboard Acceptance Evidence Template")
    $lines.Add("")
    $lines.Add("Generated: $((Get-Date).ToString("o"))")
    $lines.Add("")
    $lines.Add("This scaffold is non-mutating evidence capture. It is generated from the checked-in acceptance packs and does not require a SQL host, gateway, live Power BI session, or source database connection.")
    $lines.Add("")

    foreach ($dashboardEvidence in $Evidence) {
        $lines.Add("## $($dashboardEvidence.dashboard)")
        $lines.Add("")
        $lines.Add(("- Acceptance pack: " + [char] 0x60 + $dashboardEvidence.acceptancePack + [char] 0x60))
        $lines.Add("- Boundary: $($dashboardEvidence.boundary)")
        $lines.Add("")
        $lines.Add("| Check ID | Check | Source/control | Power BI target | Pass criteria | Expected evidence | Result | Evidence path | Reviewer | Notes |")
        $lines.Add("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        foreach ($check in $dashboardEvidence.checks) {
            $lines.Add("| $(ConvertTo-MarkdownCell $check.checkId) | $(ConvertTo-MarkdownCell $check.check) | $(ConvertTo-MarkdownCell $check.source) | $(ConvertTo-MarkdownCell $check.target) | $(ConvertTo-MarkdownCell $check.passCriteria) | $(ConvertTo-MarkdownCell $check.expectedEvidence) | Pending |  |  |  |")
        }
        $lines.Add("")
        $lines.Add("SQL-host-dependent open items:")
        foreach ($item in $dashboardEvidence.sqlHostOpenItems) {
            $lines.Add("- $item")
        }
        $lines.Add("")
    }

    return ($lines -join [Environment]::NewLine)
}

$dashboards = @(
    [pscustomobject] @{
        Key = "VmoFinance"
        Name = "VMO Finance"
        AcceptancePackPath = Join-Path $repoRoot "conductor/tracks/vmo-dashboard-completion/acceptance-pack.md"
        CheckIdPattern = "^VMO-ACC-\d{3}$"
    },
    [pscustomobject] @{
        Key = "MedicalStaff"
        Name = "Medical Staff"
        AcceptancePackPath = Join-Path $repoRoot "conductor/tracks/medical-staff-dashboard-completion/acceptance-pack.md"
        CheckIdPattern = "^MS-SAMPLE-\d{2}$"
    }
)

$selectedDashboards = @($dashboards | Where-Object { $Dashboard -eq "Both" -or $_.Key -eq $Dashboard })
foreach ($selectedDashboard in $selectedDashboards) {
    if (-not (Test-Path -LiteralPath $selectedDashboard.AcceptancePackPath)) {
        throw "Missing acceptance pack: $($selectedDashboard.AcceptancePackPath)"
    }
}

$evidence = @($selectedDashboards | ForEach-Object {
    New-DashboardAcceptanceEvidence -DashboardName $_.Name -AcceptancePackPath $_.AcceptancePackPath -CheckIdPattern $_.CheckIdPattern
})

$content = if ($Format -eq "Json") {
    [pscustomobject] [ordered] @{
        generatedAt = (Get-Date).ToString("o")
        source = "acceptance-packs"
        dashboards = $evidence
    } | ConvertTo-Json -Depth 8
}
else {
    ConvertTo-AcceptanceMarkdown -Evidence $evidence
}

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $resolvedOutputPath = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
        $OutputPath
    }
    else {
        Join-Path (Get-Location) $OutputPath
    }
    $outputDirectory = Split-Path -Parent $resolvedOutputPath
    if (-not [string]::IsNullOrWhiteSpace($outputDirectory)) {
        New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
    }
    Set-Content -LiteralPath $resolvedOutputPath -Value $content -Encoding ASCII
    Write-Host "Acceptance evidence template written: $resolvedOutputPath"
}
else {
    $content
}
