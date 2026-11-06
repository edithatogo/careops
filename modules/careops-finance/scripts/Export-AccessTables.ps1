[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $DatabasePath,

    [string[]] $ObjectName,

    [string] $OutDir = "data/extracts",

    [switch] $IncludeViews,

    [switch] $IncludeLinkedTables,

    [int] $CommandTimeoutSeconds = 120,

    [ValidateRange(0, [int]::MaxValue)]
    [int] $MaxRows = 0
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
Add-Type -AssemblyName System.Data

function Resolve-AccessProvider {
    param([string] $Path)

    foreach ($provider in @("Microsoft.ACE.OLEDB.16.0", "Microsoft.ACE.OLEDB.12.0")) {
        $connectionString = "Provider=$provider;Data Source=$Path;Persist Security Info=False;"
        $connection = [System.Data.OleDb.OleDbConnection]::new($connectionString)
        try {
            $connection.Open()
            $connection.Close()
            return $provider
        }
        catch {
            $connection.Dispose()
        }
    }

    throw "No working Microsoft ACE OLEDB provider was found for '$Path'."
}

function Quote-AccessIdentifier {
    param([string] $Name)
    return "[" + $Name.Replace("]", "]]") + "]"
}

function Get-SafeFileName {
    param([string] $Name)
    $invalid = [System.IO.Path]::GetInvalidFileNameChars()
    $safe = $Name
    foreach ($char in $invalid) {
        $safe = $safe.Replace([string] $char, "_")
    }
    return $safe
}

function Write-CsvField {
    param(
        [System.IO.StreamWriter] $Writer,
        [AllowNull()] $Value,
        [bool] $IsFirst
    )

    if (-not $IsFirst) {
        $Writer.Write(",")
    }

    if ($null -eq $Value -or $Value -is [DBNull]) {
        return
    }

    $text = [string] $Value
    if ($text.Contains('"') -or $text.Contains(",") -or $text.Contains("`r") -or $text.Contains("`n")) {
        $Writer.Write('"')
        $Writer.Write($text.Replace('"', '""'))
        $Writer.Write('"')
    }
    else {
        $Writer.Write($text)
    }
}

$resolved = (Resolve-Path -LiteralPath $DatabasePath).Path
$provider = Resolve-AccessProvider -Path $resolved
$connectionString = "Provider=$provider;Data Source=$resolved;Persist Security Info=False;"
$connection = [System.Data.OleDb.OleDbConnection]::new($connectionString)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

try {
    $connection.Open()
    $tables = $connection.GetSchema("Tables")

    $allowedTypes = @("TABLE")
    if ($IncludeViews) {
        $allowedTypes += "VIEW"
    }
    if ($IncludeLinkedTables) {
        $allowedTypes += "LINK"
    }

    $objects = foreach ($row in $tables.Rows) {
        $name = [string] $row["TABLE_NAME"]
        $type = [string] $row["TABLE_TYPE"]
        if ($name -like "MSys*" -or $type -in @("SYSTEM TABLE", "ACCESS TABLE")) {
            continue
        }
        if ($ObjectName -and $name -notin $ObjectName) {
            continue
        }
        if ($type -notin $allowedTypes) {
            continue
        }
        [pscustomobject] @{ Name = $name; Type = $type }
    }

    foreach ($object in $objects) {
        $safeName = Get-SafeFileName -Name $object.Name
        $outPath = Join-Path $OutDir "$safeName.csv"
        $command = $connection.CreateCommand()
        $command.CommandTimeout = $CommandTimeoutSeconds
        $rowLimitClause = if ($MaxRows -gt 0) { "TOP $MaxRows " } else { "" }
        $command.CommandText = "SELECT $rowLimitClause* FROM $(Quote-AccessIdentifier $object.Name)"
        $reader = $null
        $writer = $null
        $rowCount = 0

        try {
            $reader = $command.ExecuteReader()
            $writer = [System.IO.StreamWriter]::new($outPath, $false, [System.Text.UTF8Encoding]::new($false))

            for ($i = 0; $i -lt $reader.FieldCount; $i++) {
                Write-CsvField -Writer $writer -Value $reader.GetName($i) -IsFirst ($i -eq 0)
            }
            $writer.WriteLine()

            while ($reader.Read()) {
                for ($i = 0; $i -lt $reader.FieldCount; $i++) {
                    Write-CsvField -Writer $writer -Value $reader.GetValue($i) -IsFirst ($i -eq 0)
                }
                $writer.WriteLine()
                $rowCount++
            }

            [pscustomobject] @{
                ObjectName = $object.Name
                ObjectType = $object.Type
                OutputPath = (Resolve-Path -LiteralPath $outPath).Path
                RowCount = $rowCount
            }
        }
        finally {
            if ($null -ne $reader) {
                $reader.Dispose()
            }
            if ($null -ne $writer) {
                $writer.Dispose()
            }
            $command.Dispose()
        }
    }
}
finally {
    if ($connection.State -ne [System.Data.ConnectionState]::Closed) {
        $connection.Close()
    }
    $connection.Dispose()
}
