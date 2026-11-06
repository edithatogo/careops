param(
    [Parameter(Mandatory = $true)]
    [string]$Root,

    [Parameter(Mandatory = $false)]
    [string]$OutputRoot = 'data/profile/remote-dashboard-discovery',

    [Parameter(Mandatory = $false)]
    [int]$MaxItems = 20000
)

$ErrorActionPreference = 'Stop'

function Get-CandidateDashboardType {
    param([System.IO.FileSystemInfo]$Item)

    if ($Item.PSIsContainer) {
        if ($Item.Name -like '*.Report') { return 'PBIR report folder' }
        if ($Item.Name -like '*.Dataset') { return 'PBIR dataset folder' }
        if ($Item.Name -ieq 'definition' -or $Item.Name -ieq 'model-tmdl') { return 'Power BI source folder' }
        return 'Folder'
    }

    switch -Regex ($Item.Extension) {
        '^\.(pbix)$' { return 'Power BI report binary' }
        '^\.(pbit)$' { return 'Power BI template binary' }
        '^\.(pbip)$' { return 'Power BI project pointer' }
        '^\.(tmdl)$' { return 'Power BI TMDL source' }
        '^\.(json)$' { return 'Power BI/report JSON candidate' }
        '^\.(xlsx|xlsm|xls)$' { return 'Excel source candidate' }
        '^\.(accdb|mdb)$' { return 'Access source candidate' }
        default { return 'Other' }
    }
}

function Get-CandidateBusinessDomain {
    param([string]$RelativePath)

    $value = $RelativePath.ToLowerInvariant()
    if ($value -match 'vmo') { return 'VMO' }
    if ($value -match 'medical|staff|workforce|payroll|fte') { return 'Medical staff/workforce' }
    if ($value -match 'gl|ledger|account|finance') { return 'Finance/GL' }
    if ($value -match 'budget|forecast') { return 'Budget/forecast' }
    if ($value -match 'recon|reconciliation') { return 'Reconciliation' }
    return 'Unclassified'
}

if (-not (Test-Path -LiteralPath $Root)) {
    throw "Discovery root is not accessible: $Root"
}

New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$csvPath = Join-Path $OutputRoot "dashboard-inventory-$timestamp.csv"
$jsonPath = Join-Path $OutputRoot "dashboard-inventory-$timestamp.json"

$rootFullPath = [System.IO.Path]::GetFullPath($Root)
$items = New-Object System.Collections.Generic.List[object]
Get-ChildItem -LiteralPath $Root -Force -Recurse -ErrorAction Stop |
    Select-Object -First $MaxItems |
    ForEach-Object {
    $fullName = $_.FullName
    $relativePath = $fullName
    if ($fullName.StartsWith($rootFullPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        $relativePath = $fullName.Substring($rootFullPath.Length).TrimStart('\')
    }

    $length = $null
    if (-not $_.PSIsContainer) {
        $length = $_.Length
    }

    $items.Add([pscustomobject]@{
        FullPath = $fullName
        RelativePath = $relativePath
        Name = $_.Name
        Extension = $_.Extension
        ItemType = if ($_.PSIsContainer) { 'Directory' } else { 'File' }
        SizeBytes = $length
        LastWriteTime = $_.LastWriteTime.ToString('o')
        CandidateDashboardType = Get-CandidateDashboardType -Item $_
        CandidateBusinessDomain = Get-CandidateBusinessDomain -RelativePath $relativePath
        DiscoveryStatus = 'MetadataOnly'
    }) | Out-Null
}

$items | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding UTF8
$items | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

[pscustomobject]@{
    Root = $Root
    Items = $items.Count
    CsvPath = $csvPath
    JsonPath = $jsonPath
    MaxItems = $MaxItems
}
