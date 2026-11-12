[CmdletBinding(PositionalBinding = $false)]
param(
    [string[]] $DsnName = @("CA", "Magiq"),

    [string] $OutPath,

    [switch] $IncludeAllDsnValues,

    [switch] $RedactOperatorIdentity
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-PlainDictionary {
    param([Microsoft.Win32.RegistryKey] $Key)

    $values = [ordered] @{}
    foreach ($valueName in $Key.GetValueNames()) {
        $name = if ([string]::IsNullOrWhiteSpace($valueName)) { "(default)" } else { $valueName }
        $values[$name] = [string] $Key.GetValue($valueName)
    }
    return $values
}

function Redact-DsnValue {
    param(
        [string] $Name,
        [AllowNull()][string] $Value
    )

    if ($null -eq $Value) {
        return $null
    }

    if ($Name -match '(?i)(password|pwd|pass|token|secret|key|uid|user|lastuser|user id)') {
        return "<redacted>"
    }

    return $Value
}

function Get-OperatorIdentityValue {
    param([AllowNull()][string] $Value)

    if ($RedactOperatorIdentity) {
        return "<redacted>"
    }

    return $Value
}

function Select-DsnValues {
    param([System.Collections.IDictionary] $Values)

    $safeValues = [ordered] @{}
    foreach ($entry in $Values.GetEnumerator()) {
        $safeValues[$entry.Key] = Redact-DsnValue -Name $entry.Key -Value ([string] $entry.Value)
    }

    return $safeValues
}

function Get-ValueByAliases {
    param(
        [System.Collections.IDictionary] $Values,
        [string[]] $Aliases
    )

    foreach ($alias in $Aliases) {
        foreach ($entry in $Values.GetEnumerator()) {
            if ($entry.Key -eq $alias) {
                return [string] $entry.Value
            }
        }
    }

    return $null
}

function Open-RegistrySubKey {
    param(
        [Microsoft.Win32.RegistryHive] $Hive,
        [Microsoft.Win32.RegistryView] $View,
        [string] $SubKeyPath
    )

    $baseKey = [Microsoft.Win32.RegistryKey]::OpenBaseKey($Hive, $View)
    try {
        return $baseKey.OpenSubKey($SubKeyPath, $false)
    }
    finally {
        $baseKey.Close()
    }
}

function Get-OdbcDsnRegistryRecord {
    param(
        [Microsoft.Win32.RegistryHive] $Hive,
        [string] $Scope,
        [Microsoft.Win32.RegistryView] $View,
        [string] $Name
    )

    $iniPath = "SOFTWARE\ODBC\ODBC.INI"
    $dsnKey = Open-RegistrySubKey -Hive $Hive -View $View -SubKeyPath (Join-Path $iniPath $Name)
    if ($null -eq $dsnKey) {
        return $null
    }

    try {
        $values = ConvertTo-PlainDictionary -Key $dsnKey
    }
    finally {
        $dsnKey.Close()
    }

    $server = Get-ValueByAliases -Values $values -Aliases @("Server", "SERVER", "Address", "Addr", "Network")
    $database = Get-ValueByAliases -Values $values -Aliases @("Database", "DATABASE", "Initial Catalog", "DBQ")
    $driver = Get-ValueByAliases -Values $values -Aliases @("Driver", "DRIVER")
    $description = Get-ValueByAliases -Values $values -Aliases @("Description", "DESCRIPTION")
    $trustedConnection = Get-ValueByAliases -Values $values -Aliases @("Trusted_Connection", "TrustedConnection", "Integrated Security")

    $record = [ordered] @{
        dsn = $Name
        scope = $Scope
        registryView = [string] $View
        registryPath = "$Hive\$iniPath\$Name"
        found = $true
        driver = $driver
        server = $server
        database = $database
        description = $description
        trustedConnection = $trustedConnection
    }

    if ($IncludeAllDsnValues) {
        $record["redactedValues"] = Select-DsnValues -Values $values
    }

    return [pscustomobject] $record
}

function Get-OdbcDsnRecords {
    param([string[]] $Names)

    $locations = @(
        [pscustomobject] @{ Hive = [Microsoft.Win32.RegistryHive]::CurrentUser; Scope = "User" },
        [pscustomobject] @{ Hive = [Microsoft.Win32.RegistryHive]::LocalMachine; Scope = "System" }
    )
    $views = @(
        [Microsoft.Win32.RegistryView]::Registry64,
        [Microsoft.Win32.RegistryView]::Registry32
    )

    $records = New-Object System.Collections.Generic.List[object]
    foreach ($name in $Names) {
        $matched = $false
        foreach ($location in $locations) {
            foreach ($view in $views) {
                $record = Get-OdbcDsnRegistryRecord -Hive $location.Hive -Scope $location.Scope -View $view -Name $name
                if ($null -ne $record) {
                    $matched = $true
                    $records.Add($record)
                }
            }
        }

        if (-not $matched) {
            $records.Add([pscustomobject] [ordered] @{
                dsn = $name
                scope = $null
                registryView = $null
                registryPath = $null
                found = $false
                driver = $null
                server = $null
                database = $null
                description = $null
                trustedConnection = $null
            })
        }
    }

    return $records.ToArray()
}

$resolvedDsnNames = @(
    foreach ($name in $DsnName) {
        foreach ($part in ($name -split ",")) {
            if (-not [string]::IsNullOrWhiteSpace($part)) {
                $part.Trim()
            }
        }
    }
)

$sourceMappings = @(
    [pscustomobject] [ordered] @{ dashboard = "VMO Reporting"; accessObject = "ca_MVRPT_ACCOUNT"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "MVRPT_ACCOUNT" },
    [pscustomobject] [ordered] @{ dashboard = "VMO Reporting"; accessObject = "ca_MVRPT_COSTCENTRES"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "MVRPT_COSTCENTRES" },
    [pscustomobject] [ordered] @{ dashboard = "VMO Reporting"; accessObject = "dbo_FMIS_GL_JOURNAL"; dsn = "Magiq"; accessDatabaseHint = $null; sourceSchema = "dbo"; sourceObject = "FMIS_GL_JOURNAL_2026" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_FTE_EMPLOYEE_LAST_LHD_V"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "FTE_EMPLOYEE_LAST_LHD_V" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_FTE_HYPERION_LHD_V"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "FTE_HYPERION_LHD_V" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_FTE_RPT_AWARD_CODES_DIM_MV"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "FTE_RPT_AWARD_CODES_DIM_MV" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_FTE_RPT_COST_CENTRES_DIM_MV"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "FTE_RPT_COST_CENTRES_DIM_MV" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_FTE_RPT_EMP_TYPES_DIM_MV"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "FTE_RPT_EMP_TYPES_DIM_MV" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_FTE_RPT_PAYCLASS_DIM_MV"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "FTE_RPT_PAYCLASS_DIM_MV" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "ca_MVRPT_COSTCENTRES"; dsn = "CA"; accessDatabaseHint = "WORKFORCE"; sourceSchema = "ca"; sourceObject = "MVRPT_COSTCENTRES" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "dbo_FTE_IS_EMPLOYEE_INT"; dsn = "Magiq"; accessDatabaseHint = "MAGIQ_PRD"; sourceSchema = "dbo"; sourceObject = "FTE_IS_EMPLOYEE_INT" },
    [pscustomobject] [ordered] @{ dashboard = "Medical Staff Reporting"; accessObject = "dbo_FTE_IS_PAYROLL_INT"; dsn = "Magiq"; accessDatabaseHint = "MAGIQ_PRD"; sourceSchema = "dbo"; sourceObject = "FTE_IS_PAYROLL_INT" }
)

$dsnRecords = Get-OdbcDsnRecords -Names $resolvedDsnNames
$payload = [pscustomobject] [ordered] @{
    generatedAt = (Get-Date).ToString("o")
    computerName = Get-OperatorIdentityValue -Value $env:COMPUTERNAME
    currentUser = Get-OperatorIdentityValue -Value ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
    method = "Read-only registry inspection of HKCU/HKLM ODBC.INI in 64-bit and 32-bit registry views; no SQL connection attempted."
    evidenceHandling = "Generated output is intended for ignored data/profile evidence. DSN values are limited to safe summary fields unless IncludeAllDsnValues is supplied; sensitive DSN keys are redacted."
    dsnRecords = @($dsnRecords)
    sourceMappings = @($sourceMappings | Where-Object { $_.dsn -in $resolvedDsnNames })
    mappingRule = "Match Access linked-table DSN to the ODBC DSN record. The DSN record supplies server and default database when configured; Access metadata supplies dashboard, Access object, database hint, schema, and object."
}

if ([string]::IsNullOrWhiteSpace($OutPath)) {
    $payload
}
else {
    $resolvedOutPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutPath)
    $outDir = Split-Path -Parent $resolvedOutPath
    if (-not [string]::IsNullOrWhiteSpace($outDir)) {
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    }

    $payload | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $resolvedOutPath -Encoding UTF8
    [pscustomobject] @{
        outputPath = $resolvedOutPath
        dsnCount = @($dsnRecords | Where-Object { $_.found }).Count
        sourceMappingCount = @($payload.sourceMappings).Count
    }
}
