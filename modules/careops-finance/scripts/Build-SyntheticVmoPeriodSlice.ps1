[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $FixturePath,
    [Parameter(Mandatory = $true)]
    [string] $OutputPath,
    [Parameter(Mandatory = $true)]
    [datetime] $AsOfDate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-Result {
    param([string] $Status, [string] $Reason)
    return [ordered]@{
        schemaVersion = 1
        fixtureId = $fixture.fixtureId
        sourceKind = "synthetic"
        productionBinding = $false
        status = $Status
        reason = $Reason
        snapshotDate = $fixture.snapshotDate
        periods = @()
        annual = $null
    }
}

$fixture = Get-Content -LiteralPath $FixturePath -Raw | ConvertFrom-Json
$result = $null

if (-not $fixture.providerAvailable) {
    $result = New-Result -Status "ProviderAbsent" -Reason "Optional synthetic provider is not available; fail closed with an empty slice."
}
elseif ([int]$fixture.contractVersion -ne 1) {
    $result = New-Result -Status "IncompatibleVersion" -Reason "Provider contract version is not supported."
}
else {
    $snapshotDate = [datetime]::ParseExact([string]$fixture.snapshotDate, "yyyy-MM-dd", [Globalization.CultureInfo]::InvariantCulture)
    if (($AsOfDate.Date - $snapshotDate.Date).TotalDays -gt [double]$fixture.maxAgeDays) {
        $result = New-Result -Status "Stale" -Reason "Provider snapshot exceeds the fixture freshness limit."
    }
    elseif (@($fixture.periods).Count -eq 0 -or @($fixture.glRows).Count -eq 0 -or @($fixture.vmoRows).Count -eq 0) {
        $result = New-Result -Status "MissingInput" -Reason "Calendar and both fact inputs are required."
    }
    else {
        $periodByKey = @{}
        foreach ($period in $fixture.periods) {
            if ([string]::IsNullOrWhiteSpace([string]$period.periodKey) -or $periodByKey.ContainsKey([string]$period.periodKey)) {
                $result = New-Result -Status "InvalidPeriodKey" -Reason "Calendar period keys must be present and unique."
                break
            }
            $periodByKey[[string]$period.periodKey] = $period
        }

        if ($null -eq $result) {
            $deduplicated = @{}
            foreach ($sourceName in @("glRows", "vmoRows")) {
                foreach ($row in $fixture.$sourceName) {
                    if ([string]::IsNullOrWhiteSpace([string]$row.factId) -or [string]::IsNullOrWhiteSpace([string]$row.periodKey) -or $null -eq $row.amount) {
                        $result = New-Result -Status "MissingInput" -Reason "Fact identity, period identity, and amount are required."
                        break
                    }
                    if (-not $periodByKey.ContainsKey([string]$row.periodKey)) {
                        $result = New-Result -Status "UnmappedPeriod" -Reason "A fact period key has no matching calendar row."
                        break
                    }
                    $dedupeKey = "$sourceName|$($row.factId)"
                    $serialized = "$($row.periodKey)|$([string]$row.amount)"
                    if ($deduplicated.ContainsKey($dedupeKey)) {
                        if ($deduplicated[$dedupeKey] -ne $serialized) {
                            $result = New-Result -Status "DuplicateConflict" -Reason "A retried fact identity arrived with different content."
                            break
                        }
                        continue
                    }
                    $deduplicated[$dedupeKey] = $serialized
                }
                if ($null -ne $result) { break }
            }

            if ($null -eq $result) {
                $periodResults = foreach ($period in @($fixture.periods | Sort-Object sortOrder)) {
                    $glTotal = [double](($fixture.glRows | Where-Object { $_.periodKey -eq $period.periodKey } | Group-Object factId | ForEach-Object { [double]$_.Group[0].amount } | Measure-Object -Sum).Sum)
                    $vmoTotal = [double](($fixture.vmoRows | Where-Object { $_.periodKey -eq $period.periodKey } | Group-Object factId | ForEach-Object { [double]$_.Group[0].amount } | Measure-Object -Sum).Sum)
                    [ordered]@{
                        periodKey = [string]$period.periodKey
                        financialYear = [string]$period.financialYear
                        financialPeriod = [string]$period.financialPeriod
                        glAmount = [math]::Round($glTotal, 2)
                        vmoAmount = [math]::Round($vmoTotal, 2)
                        variance = [math]::Round($vmoTotal - $glTotal, 2)
                    }
                }
                $glAnnual = [double](($periodResults | ForEach-Object { [double]$_.glAmount } | Measure-Object -Sum).Sum)
                $vmoAnnual = [double](($periodResults | ForEach-Object { [double]$_.vmoAmount } | Measure-Object -Sum).Sum)
                $result = New-Result -Status "Ready" -Reason "Synthetic period-keyed reconciliation; no production source or ledger authority is used."
                $result.periods = @($periodResults)
                $result.annual = [ordered]@{
                    glAmount = [math]::Round($glAnnual, 2)
                    vmoAmount = [math]::Round($vmoAnnual, 2)
                    variance = [math]::Round($vmoAnnual - $glAnnual, 2)
                }
            }
        }
    }
}

$outputDirectory = Split-Path -Parent $OutputPath
if (-not [string]::IsNullOrWhiteSpace($outputDirectory)) {
    New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding utf8
