[CmdletBinding()]
param(
    [switch] $WriteEvidence,

    [string] $EvidenceOutPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$scriptPath = Join-Path $repoRoot "scripts\Get-OdbcDsnSourceContract.ps1"
$discoveryDocPath = Join-Path $repoRoot "docs\sql-source-discovery.md"
if ([string]::IsNullOrWhiteSpace($EvidenceOutPath)) {
    $EvidenceOutPath = Join-Path $repoRoot "data\profile\odbc-dsn-source-contract.evidence.json"
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

function Normalize-NullableText {
    param([AllowNull()][string] $Value)

    if ($null -eq $Value) {
        return $null
    }

    $trimmed = $Value.Trim().Trim([char] 0x60)
    if ($trimmed -eq "not exposed in Access connect string") {
        return $null
    }

    return $trimmed
}

function Get-RowKey {
    param([pscustomobject] $Row)

    return (@(
        $Row.dashboard
        $Row.accessObject
        $Row.dsn
        (Normalize-NullableText $Row.accessDatabaseHint)
        $Row.sourceSchema
        $Row.sourceObject
    ) -join "|")
}

function Get-DocumentedAccessDsnMappings {
    param([string] $Path)

    $lines = Get-Content -LiteralPath $Path
    $startIndex = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -eq "Current Access-derived object mappings:") {
            $startIndex = $i + 1
            break
        }
    }

    Assert-Condition ($startIndex -ge 0) "Could not find Current Access-derived object mappings table in docs/sql-source-discovery.md"

    $rows = New-Object System.Collections.Generic.List[object]
    for ($i = $startIndex; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ([string]::IsNullOrWhiteSpace($line)) {
            if ($rows.Count -gt 0) {
                break
            }

            continue
        }

        if ($line -notmatch '^\|') {
            continue
        }

        if ($line -match '^\|\s*-') {
            continue
        }

        $cells = @(($line.Trim("|") -split "\|") | ForEach-Object { $_.Trim() })
        if ($cells[0] -eq "Dashboard") {
            continue
        }

        Assert-Condition ($cells.Count -eq 6) "Unexpected mapping table column count in docs/sql-source-discovery.md: $line"
        $rows.Add([pscustomobject] [ordered] @{
            dashboard = Normalize-NullableText $cells[0]
            accessObject = Normalize-NullableText $cells[1]
            dsn = Normalize-NullableText $cells[2]
            accessDatabaseHint = Normalize-NullableText $cells[3]
            sourceSchema = Normalize-NullableText $cells[4]
            sourceObject = Normalize-NullableText $cells[5]
        })
    }

    return $rows.ToArray()
}

function Assert-HasProperties {
    param(
        [object] $Object,
        [string[]] $Properties,
        [string] $Context
    )

    $actual = @($Object.PSObject.Properties.Name)
    foreach ($property in $Properties) {
        Assert-Condition ($property -in $actual) "$Context missing property: $property"
    }
}

Assert-Condition (Test-Path -LiteralPath $scriptPath) "Missing DSN source contract script: $scriptPath"
Assert-Condition (Test-Path -LiteralPath $discoveryDocPath) "Missing SQL source discovery doc: $discoveryDocPath"

$payload = & $scriptPath -DsnName @("CA", "Magiq")

Assert-HasProperties -Object $payload -Context "DSN payload" -Properties @(
    "generatedAt",
    "computerName",
    "currentUser",
    "method",
    "evidenceHandling",
    "dsnRecords",
    "sourceMappings",
    "mappingRule"
)

$records = @($payload.dsnRecords)
Assert-Condition ($records.Count -ge 2) "Expected at least one DSN record each for CA and Magiq; got $($records.Count)"
foreach ($dsnName in @("CA", "Magiq")) {
    $matching = @($records | Where-Object { $_.dsn -eq $dsnName })
    Assert-Condition ($matching.Count -ge 1) "Expected at least one DSN record for $dsnName"
}

foreach ($record in $records) {
    Assert-HasProperties -Object $record -Context "DSN record $($record.dsn)" -Properties @(
        "dsn",
        "scope",
        "registryView",
        "registryPath",
        "found",
        "driver",
        "server",
        "database",
        "description",
        "trustedConnection"
    )

    Assert-Condition ($record.dsn -in @("CA", "Magiq")) "Unexpected DSN record name: $($record.dsn)"
    Assert-Condition ($record.found -is [bool]) "DSN record $($record.dsn) found property must be Boolean"
}

$redactedPayload = & $scriptPath -DsnName @("CA", "Magiq") -IncludeAllDsnValues -RedactOperatorIdentity
Assert-Condition ($redactedPayload.computerName -eq "<redacted>") "Redacted payload should redact computerName"
Assert-Condition ($redactedPayload.currentUser -eq "<redacted>") "Redacted payload should redact currentUser"
foreach ($record in @($redactedPayload.dsnRecords | Where-Object { $_.found })) {
    if ("redactedValues" -in @($record.PSObject.Properties.Name)) {
        foreach ($entry in $record.redactedValues.PSObject.Properties) {
            if ($entry.Name -match '(?i)(password|pwd|pass|token|secret|key|uid|user|lastuser|user id)') {
                Assert-Condition ($entry.Value -eq "<redacted>") "Sensitive DSN value $($entry.Name) should be redacted"
            }
        }
    }
}

$missingDsnNames = @("__FinanceDbMissingDsn_CA__", "__FinanceDbMissingDsn_Magiq__")
$missingPayload = & $scriptPath -DsnName $missingDsnNames
$missingRecords = @($missingPayload.dsnRecords)
Assert-Condition ($missingRecords.Count -eq $missingDsnNames.Count) "Missing-DSN fallback should emit one row per requested DSN"
foreach ($missingDsnName in $missingDsnNames) {
    $record = @($missingRecords | Where-Object { $_.dsn -eq $missingDsnName })
    Assert-Condition ($record.Count -eq 1) "Missing-DSN fallback did not emit exactly one row for $missingDsnName"
    Assert-Condition ($record[0].found -eq $false) "Missing-DSN fallback for $missingDsnName should set found to false"
    foreach ($emptyProperty in @("scope", "registryView", "registryPath", "driver", "server", "database", "description", "trustedConnection")) {
        Assert-Condition ($null -eq $record[0].$emptyProperty) "Missing-DSN fallback for $missingDsnName should leave $emptyProperty null"
    }
}

$documentedMappings = @(Get-DocumentedAccessDsnMappings -Path $discoveryDocPath)
$scriptMappings = @($payload.sourceMappings)
Assert-Condition ($scriptMappings.Count -eq 12) "Expected 12 script source mappings for CA/Magiq; got $($scriptMappings.Count)"
Assert-Condition ($documentedMappings.Count -eq $scriptMappings.Count) "Documented mapping count $($documentedMappings.Count) does not match script mapping count $($scriptMappings.Count)"

foreach ($mapping in $scriptMappings) {
    Assert-HasProperties -Object $mapping -Context "source mapping $($mapping.accessObject)" -Properties @(
        "dashboard",
        "accessObject",
        "dsn",
        "accessDatabaseHint",
        "sourceSchema",
        "sourceObject"
    )

    Assert-Condition ($mapping.dsn -in @("CA", "Magiq")) "Unexpected DSN in source mapping: $($mapping.dsn)"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($mapping.dashboard)) "Source mapping has blank dashboard"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($mapping.accessObject)) "Source mapping has blank Access object"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($mapping.sourceSchema)) "Source mapping has blank source schema"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($mapping.sourceObject)) "Source mapping has blank source object"
}

$documentedKeys = @($documentedMappings | ForEach-Object { Get-RowKey $_ } | Sort-Object)
$scriptKeys = @($scriptMappings | ForEach-Object { Get-RowKey $_ } | Sort-Object)
Compare-Object -ReferenceObject $documentedKeys -DifferenceObject $scriptKeys | ForEach-Object {
    throw "Documented Access-derived SQL/DSN mappings do not match Get-OdbcDsnSourceContract.ps1 output: $($_.InputObject)"
}

if ($WriteEvidence) {
    $evidenceResult = & $scriptPath -DsnName @("CA", "Magiq") -IncludeAllDsnValues -RedactOperatorIdentity -OutPath $EvidenceOutPath
    Assert-Condition (Test-Path -LiteralPath $evidenceResult.outputPath) "Evidence file was not written: $($evidenceResult.outputPath)"

    $evidenceJson = Get-Content -LiteralPath $evidenceResult.outputPath -Raw | ConvertFrom-Json
    Assert-Condition ($evidenceJson.computerName -eq "<redacted>") "Evidence file should redact computerName"
    Assert-Condition ($evidenceJson.currentUser -eq "<redacted>") "Evidence file should redact currentUser"
    Assert-Condition (@($evidenceJson.sourceMappings).Count -eq 12) "Evidence file should include 12 source mappings"

    Write-Host "ODBC DSN source contract evidence: $($evidenceResult.outputPath)"
}

Write-Host "ODBC DSN source contract validation: OK"
