[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
    [string[]] $DatabasePath,

    [string] $OutDir = "data/profile",

    [switch] $IncludeSystemObjects,

    [switch] $IncludeRowCounts,

    [int] $CommandTimeoutSeconds = 30
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

        $providers = @(
            "Microsoft.ACE.OLEDB.16.0",
            "Microsoft.ACE.OLEDB.12.0"
        )

        foreach ($provider in $providers) {
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

        throw "No working Microsoft ACE OLEDB provider was found for '$Path'. Install the Microsoft Access Database Engine or run on a machine with Office/Access database drivers."
}

function Quote-AccessIdentifier {
    param([string] $Name)
    return "[" + $Name.Replace("]", "]]") + "]"
}

function Get-AccessObjectCategory {
    param([string] $Type)

    switch ($Type) {
        "TABLE" { "local-table" }
        "VIEW" { "saved-query" }
        "LINK" { "linked-table" }
        "PASS-THROUGH" { "pass-through-query" }
        "SYSTEM TABLE" { "system-table" }
        "ACCESS TABLE" { "access-table" }
        default { "other" }
    }
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

function Get-ReaderColumnSchema {
    param(
        [System.Data.OleDb.OleDbConnection] $Connection,
        [string] $ObjectName,
        [int] $TimeoutSeconds
    )

    $command = $Connection.CreateCommand()
    $reader = $null
    try {
        $command.CommandTimeout = $TimeoutSeconds
        $command.CommandText = "SELECT * FROM $(Quote-AccessIdentifier $ObjectName) WHERE 1 = 0"
        $reader = $command.ExecuteReader()
        $schema = $reader.GetSchemaTable()
        @(
            foreach ($column in $schema.Rows) {
                [ordered] @{
                    name = [string] $column["ColumnName"]
                    ordinal = if ($column["ColumnOrdinal"] -is [DBNull]) { $null } else { [int] $column["ColumnOrdinal"] }
                    dataType = if ($column["ProviderType"] -is [DBNull]) { $null } else { [int] $column["ProviderType"] }
                    nullable = if ($column["AllowDBNull"] -is [DBNull]) { $null } else { [bool] $column["AllowDBNull"] }
                    maxLength = if ($column["ColumnSize"] -is [DBNull]) { $null } else { [int] $column["ColumnSize"] }
                }
            }
        )
    }
    finally {
        if ($null -ne $reader) {
            $reader.Dispose()
        }
        $command.Dispose()
    }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

foreach ($database in $DatabasePath) {
        $resolved = (Resolve-Path -LiteralPath $database).Path
        $provider = Resolve-AccessProvider -Path $resolved
        $connectionString = "Provider=$provider;Data Source=$resolved;Persist Security Info=False;"
        $connection = [System.Data.OleDb.OleDbConnection]::new($connectionString)

        try {
            $connection.Open()
            $tables = $connection.GetSchema("Tables")

            $objects = foreach ($row in $tables.Rows) {
                $name = [string] $row["TABLE_NAME"]
                $type = [string] $row["TABLE_TYPE"]
                if (-not $IncludeSystemObjects -and ($name -like "MSys*" -or $type -in @("SYSTEM TABLE", "ACCESS TABLE"))) {
                    continue
                }

                $columnError = $null
                $objectColumns = @()
                try {
                    $columnSchema = $connection.GetSchema("Columns", @($null, $null, $name, $null))
                    $objectColumns = @(
                        foreach ($column in $columnSchema.Rows) {
                            [ordered] @{
                                name = [string] $column["COLUMN_NAME"]
                                ordinal = if ($column["ORDINAL_POSITION"] -is [DBNull]) { $null } else { [int] $column["ORDINAL_POSITION"] }
                                dataType = if ($column["DATA_TYPE"] -is [DBNull]) { $null } else { [int] $column["DATA_TYPE"] }
                                nullable = if ($column["IS_NULLABLE"] -is [DBNull]) { $null } else { [bool] $column["IS_NULLABLE"] }
                                maxLength = if ($column["CHARACTER_MAXIMUM_LENGTH"] -is [DBNull]) { $null } else { [int] $column["CHARACTER_MAXIMUM_LENGTH"] }
                            }
                        }
                    )
                }
                catch {
                    $columnError = $_.Exception.Message
                }

                if ($objectColumns.Count -eq 0 -and $type -in @("TABLE", "VIEW", "LINK")) {
                    try {
                        $objectColumns = Get-ReaderColumnSchema -Connection $connection -ObjectName $name -TimeoutSeconds $CommandTimeoutSeconds
                        if ($objectColumns.Count -gt 0) {
                            $columnError = $null
                        }
                    }
                    catch {
                        $columnError = $_.Exception.Message
                    }
                }

                $rowCount = $null
                $rowCountError = $null
                if ($IncludeRowCounts -and $type -in @("TABLE", "LINK")) {
                    $command = $connection.CreateCommand()
                    $command.CommandTimeout = $CommandTimeoutSeconds
                    $command.CommandText = "SELECT COUNT(*) FROM $(Quote-AccessIdentifier $name)"
                    try {
                        $rowCount = [int64] $command.ExecuteScalar()
                    }
                    catch {
                        $rowCountError = $_.Exception.Message
                    }
                    finally {
                        $command.Dispose()
                    }
                }

                [pscustomobject] [ordered] @{
                    name = $name
                    type = $type
                    objectCategory = Get-AccessObjectCategory -Type $type
                    isLocalTable = ($type -eq "TABLE")
                    isExportable = ($type -eq "TABLE")
                    columnCount = $objectColumns.Count
                    columnError = $columnError
                    rowCount = $rowCount
                    rowCountError = $rowCountError
                    columns = $objectColumns
                }
            }

            $inventory = [ordered] @{
                database = [System.IO.Path]::GetFileName($resolved)
                databasePath = $resolved
                provider = $provider
                generatedAt = (Get-Date).ToString("o")
                includeSystemObjects = [bool] $IncludeSystemObjects
                includeRowCounts = [bool] $IncludeRowCounts
                objectCount = @($objects).Count
                objects = @($objects)
            }

            $baseName = [System.IO.Path]::GetFileNameWithoutExtension($resolved)
            $outPath = Join-Path $OutDir "$(Get-SafeFileName $baseName).inventory.json"
            ([pscustomobject] $inventory) | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outPath -Encoding UTF8
            [pscustomobject] @{
                database = $inventory.database
                provider = $inventory.provider
                objectCount = $inventory.objectCount
                inventoryPath = (Resolve-Path -LiteralPath $outPath).Path
            }
        }
        finally {
            if ($connection.State -ne [System.Data.ConnectionState]::Closed) {
                $connection.Close()
            }
            $connection.Dispose()
        }
}
