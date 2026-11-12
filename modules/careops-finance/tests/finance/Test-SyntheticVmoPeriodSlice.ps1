[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "../..")).Path
$builder = Join-Path $repoRoot "scripts/Build-SyntheticVmoPeriodSlice.ps1"
$fixturePath = Join-Path $repoRoot "tests/fixtures/finance/synthetic-vmo-period-reconciliation-v1.json"
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null

function Assert-Equal {
    param($Expected, $Actual, [string] $Message)
    if ($Expected -is [array] -or $Actual -is [array]) {
        $expectedItems = @($Expected)
        $actualItems = @($Actual)
        if ($expectedItems.Count -ne $actualItems.Count) { throw $Message }
        for ($index = 0; $index -lt $expectedItems.Count; $index++) {
            if ($expectedItems[$index] -is [string]) {
                if ([string]$expectedItems[$index] -ne [string]$actualItems[$index]) { throw $Message }
            }
            elseif ([math]::Abs([double]$expectedItems[$index] - [double]$actualItems[$index]) -gt 0.000001) {
                throw $Message
            }
        }
    }
    elseif ($Expected -ne $Actual) {
        throw "$Message Expected '$Expected'; got '$Actual'."
    }
}

function Invoke-FixtureCase {
    param($Fixture, [datetime] $AsOfDate, [string] $Name)
    $caseFixture = Join-Path $tempRoot "$Name.fixture.json"
    $caseOutput = Join-Path $tempRoot "$Name.output.json"
    $Fixture | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $caseFixture -Encoding utf8
    & $builder -FixturePath $caseFixture -OutputPath $caseOutput -AsOfDate $AsOfDate
    return Get-Content -LiteralPath $caseOutput -Raw | ConvertFrom-Json
}

try {
    $fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
    $valid = Invoke-FixtureCase -Fixture $fixture -AsOfDate ([datetime]"2026-10-25") -Name "valid"
    Assert-Equal "Ready" $valid.status "Synthetic source should produce a slice."
    Assert-Equal $false $valid.productionBinding "Synthetic output must remain explicitly unbound from production."
    Assert-Equal @("2025-26|Jul", "2025-26|Aug", "2025-26|Sep") @($valid.periods | ForEach-Object { $_.periodKey }) "Calendar keys and sort order must be preserved."
    Assert-Equal @(41000, 37000, 29000) @($valid.periods | ForEach-Object { [double]$_.glAmount }) "Monthly GL totals must reconcile to the fixture."
    Assert-Equal @(42000, 36500, 28500) @($valid.periods | ForEach-Object { [double]$_.vmoAmount }) "Monthly VMO totals must reconcile to the fixture."
    Assert-Equal @(1000, -500, -500) @($valid.periods | ForEach-Object { [double]$_.variance }) "Monthly variances must be visible even when annual totals cancel."
    Assert-Equal 107000 ([double]$valid.annual.glAmount) "Annual GL amount is incorrect."
    Assert-Equal 107000 ([double]$valid.annual.vmoAmount) "Annual VMO amount is incorrect."
    Assert-Equal 0 ([double]$valid.annual.variance) "Annual variance is incorrect."

    $absent = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $absent.providerAvailable = $false
    $absentResult = Invoke-FixtureCase -Fixture $absent -AsOfDate ([datetime]"2026-10-25") -Name "absent"
    Assert-Equal "ProviderAbsent" $absentResult.status "Missing optional providers must fail closed."
    Assert-Equal 0 @($absentResult.periods).Count "Absent provider must produce no rows."

    $incompatible = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $incompatible.contractVersion = 2
    $incompatibleResult = Invoke-FixtureCase -Fixture $incompatible -AsOfDate ([datetime]"2026-10-25") -Name "incompatible"
    Assert-Equal "IncompatibleVersion" $incompatibleResult.status "Incompatible versions must be rejected."

    $stale = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $stale.snapshotDate = "2026-09-01"
    $staleResult = Invoke-FixtureCase -Fixture $stale -AsOfDate ([datetime]"2026-10-25") -Name "stale"
    Assert-Equal "Stale" $staleResult.status "Stale snapshots must be rejected."

    $missingPeriod = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $missingPeriod.glRows[0].periodKey = ""
    $missingResult = Invoke-FixtureCase -Fixture $missingPeriod -AsOfDate ([datetime]"2026-10-25") -Name "missing-period"
    Assert-Equal "MissingInput" $missingResult.status "Missing period identity must be rejected."

    $unmappedPeriod = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $unmappedPeriod.vmoRows[0].periodKey = "2025-26|Oct"
    $unmappedResult = Invoke-FixtureCase -Fixture $unmappedPeriod -AsOfDate ([datetime]"2026-10-25") -Name "unmapped-period"
    Assert-Equal "UnmappedPeriod" $unmappedResult.status "Facts outside the calendar must be rejected."

    $missingInput = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $missingInput.vmoRows = @()
    $missingInputResult = Invoke-FixtureCase -Fixture $missingInput -AsOfDate ([datetime]"2026-10-25") -Name "missing-input"
    Assert-Equal "MissingInput" $missingInputResult.status "Missing fact tables must be rejected."

    $duplicateRetry = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $duplicateRetry.glRows += $fixture.glRows[0]
    $duplicateResult = Invoke-FixtureCase -Fixture $duplicateRetry -AsOfDate ([datetime]"2026-10-25") -Name "duplicate-retry"
    Assert-Equal "Ready" $duplicateResult.status "An identical retry should be idempotent."
    Assert-Equal (ConvertTo-Json -InputObject $valid.periods -Compress -Depth 8) (ConvertTo-Json -InputObject $duplicateResult.periods -Compress -Depth 8) "Duplicate retry changed the report slice."

    $duplicateConflict = $fixture | ConvertTo-Json -Depth 8 | ConvertFrom-Json
    $conflictingRow = $fixture.glRows[0] | ConvertTo-Json -Depth 4 | ConvertFrom-Json
    $conflictingRow.amount = 41001.0
    $duplicateConflict.glRows += $conflictingRow
    $conflictResult = Invoke-FixtureCase -Fixture $duplicateConflict -AsOfDate ([datetime]"2026-10-25") -Name "duplicate-conflict"
    Assert-Equal "DuplicateConflict" $conflictResult.status "Changed content under a retried identity must be rejected."

    Write-Host "Synthetic VMO period slice contract: OK"
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
