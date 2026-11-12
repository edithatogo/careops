[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true, ValueFromPipeline = $true, ValueFromRemainingArguments = $true)]
    [string[]] $DatabasePath,

    [string] $OutDir = "data/profile",

    [switch] $IncludeNonSqlHints
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

function Get-SafeFileName {
    param([string] $Name)

    $invalid = [System.IO.Path]::GetInvalidFileNameChars()
    $safe = $Name
    foreach ($char in $invalid) {
        $safe = $safe.Replace([string] $char, "_")
    }
    return $safe
}

function Redact-SecretText {
    param([AllowNull()][string] $Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $Text
    }

    $redacted = $Text
    $patterns = @(
        '(?i)(password|pwd|pass|token|secret|key)\s*=\s*([^;\r\n]+)',
        '(?i)(uid|user id|user)\s*=\s*([^;\r\n]+)'
    )
    foreach ($pattern in $patterns) {
        $redacted = [regex]::Replace($redacted, $pattern, {
            param($match)
            return "$($match.Groups[1].Value)=<redacted>"
        })
    }
    return $redacted
}

function Split-ConnectionString {
    param([AllowNull()][string] $Connect)

    $parts = [ordered] @{}
    if ([string]::IsNullOrWhiteSpace($Connect)) {
        return $parts
    }

    foreach ($part in ($Connect -split ';')) {
        if ([string]::IsNullOrWhiteSpace($part)) {
            continue
        }
        $index = $part.IndexOf('=')
        if ($index -lt 1) {
            $parts[$part.Trim()] = $true
            continue
        }

        $name = $part.Substring(0, $index).Trim()
        $value = $part.Substring($index + 1).Trim()
        if ($name -match '^(?i)(password|pwd|pass|token|secret|key|uid|user id|user)$') {
            $value = '<redacted>'
        }
        $parts[$name] = $value
    }

    return $parts
}

function Get-ConnectionHints {
    param(
        [AllowNull()][string] $Connect,
        [AllowNull()][string] $SourceTableName
    )

    $parts = Split-ConnectionString -Connect $Connect
    $serverKeys = @('SERVER', 'DATA SOURCE', 'ADDRESS', 'ADDR', 'NETWORK ADDRESS')
    $databaseKeys = @('DATABASE', 'INITIAL CATALOG', 'DBQ')
    $driverKeys = @('DRIVER', 'PROVIDER')
    $server = $null
    $database = $null
    $driver = $null
    $dsn = $null

    foreach ($entry in $parts.GetEnumerator()) {
        $key = $entry.Key.ToUpperInvariant()
        if ($null -eq $server -and $key -in $serverKeys) {
            $server = [string] $entry.Value
        }
        if ($null -eq $database -and $key -in $databaseKeys) {
            $database = [string] $entry.Value
        }
        if ($null -eq $driver -and $key -in $driverKeys) {
            $driver = [string] $entry.Value
        }
        if ($key -eq 'DSN') {
            $dsn = [string] $entry.Value
        }
    }

    $schema = $null
    $object = $SourceTableName
    if (-not [string]::IsNullOrWhiteSpace($SourceTableName)) {
        $clean = $SourceTableName.Trim()
        $tokens = $clean -split '\.'
        if ($tokens.Count -ge 2) {
            $schema = $tokens[$tokens.Count - 2].Trim('[', ']')
            $object = $tokens[$tokens.Count - 1].Trim('[', ']')
        }
    }

    return [ordered] @{
        server = $server
        database = $database
        driver = $driver
        dsn = $dsn
        schema = $schema
        object = $object
        redactedConnect = Redact-SecretText -Text $Connect
        parsedConnect = $parts
    }
}

function Test-SqlLikeSource {
    param(
        [AllowNull()][string] $Connect,
        [AllowNull()][string] $Sql
    )

    $combined = "$Connect`n$Sql"
    return ($combined -match '(?i)(sql server|sqloledb|sqlncli|msodbcsql|odbc;|dsn=|server=|initial catalog=|driver=.*sql)')
}

function Get-AccessSourcesWithDao {
    param([string] $Path)

    $engine = $null
    $database = $null
    $records = New-Object System.Collections.Generic.List[object]
    try {
        $engine = New-Object -ComObject DAO.DBEngine.120
        $database = $engine.OpenDatabase($Path, $false, $true)

        foreach ($tableDef in $database.TableDefs) {
            $name = [string] $tableDef.Name
            if ($name -like 'MSys*') {
                continue
            }

            $connect = [string] $tableDef.Connect
            $sourceTableName = [string] $tableDef.SourceTableName
            if (-not $IncludeNonSqlHints -and -not (Test-SqlLikeSource -Connect $connect -Sql $null)) {
                continue
            }

            $hints = Get-ConnectionHints -Connect $connect -SourceTableName $sourceTableName
            $records.Add([pscustomobject] [ordered] @{
                objectName = $name
                objectType = 'tabledef'
                sourceTableName = $sourceTableName
                sql = $null
                hints = $hints
            })
        }

        foreach ($queryDef in $database.QueryDefs) {
            $name = [string] $queryDef.Name
            if ($name -like '~*' -or $name -like 'MSys*') {
                continue
            }

            $connect = [string] $queryDef.Connect
            $sql = [string] $queryDef.SQL
            if (-not $IncludeNonSqlHints -and -not (Test-SqlLikeSource -Connect $connect -Sql $sql)) {
                continue
            }

            $hints = Get-ConnectionHints -Connect $connect -SourceTableName $null
            $records.Add([pscustomobject] [ordered] @{
                objectName = $name
                objectType = 'querydef'
                sourceTableName = $null
                sql = Redact-SecretText -Text $sql
                hints = $hints
            })
        }
    }
    finally {
        if ($null -ne $database) {
            $database.Close()
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($database)
        }
        if ($null -ne $engine) {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($engine)
        }
    }

    return $records.ToArray()
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

foreach ($database in $DatabasePath) {
    $resolved = (Resolve-Path -LiteralPath $database).Path
    $sources = Get-AccessSourcesWithDao -Path $resolved
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolved)
    $outPath = Join-Path $OutDir "$(Get-SafeFileName $baseName).sql-sources.json"

    $payload = [ordered] @{
        database = [System.IO.Path]::GetFileName($resolved)
        databasePath = $resolved
        generatedAt = (Get-Date).ToString('o')
        method = 'DAO.DBEngine.OpenDatabase(readOnly=True)'
        includeNonSqlHints = [bool] $IncludeNonSqlHints
        sourceCount = @($sources).Count
        sources = @($sources)
    }

    ([pscustomobject] $payload) | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outPath -Encoding UTF8
    [pscustomobject] @{
        database = $payload.database
        sourceCount = $payload.sourceCount
        outputPath = (Resolve-Path -LiteralPath $outPath).Path
    }
}
