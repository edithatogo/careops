[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString('N'))
$global:FinancePreviewMock = @()
$savedToken = $env:GH_TOKEN
$env:GH_TOKEN = 'fictional-read-only-workflow-token'
$global:FinancePreviewHeaders = $null
function Invoke-RestMethod { param($Uri, $TimeoutSec, $Headers)
    if ($Uri -cne 'https://api.github.com/repos/PowerShell/PowerShell/releases?per_page=100') { throw 'Unexpected authenticated endpoint.' }
    $global:FinancePreviewHeaders = $Headers
    return $global:FinancePreviewMock
}
function Invoke-WebRequest { param($Uri, $OutFile, $TimeoutSec) Set-Content -LiteralPath $OutFile -Value 'inert damaged archive' }
function New-Release([string]$Version) {
    $name = "PowerShell-$Version-win-x64.zip"
    return [pscustomobject]@{
        tag_name = "v$Version"; prerelease = $true; draft = $false
        assets = @([pscustomobject]@{
            name = $name; digest = ('sha256:' + ('a' * 64))
            browser_download_url = "https://github.com/PowerShell/PowerShell/releases/download/v$Version/$name"
        })
    }
}
try {
    $global:FinancePreviewMock = @((New-Release '7.7.0-preview.9'), (New-Release '7.7.0-preview.10'))
    & "$PSScriptRoot/Resolve-PowerShellPreview.ps1" -OutputDirectory $root -ResolveOnly
    if ($global:FinancePreviewHeaders.Authorization -cne "Bearer $env:GH_TOKEN") { throw 'Read-only workflow authentication missing.' }
    $receipt = Get-Content "$root/candidate.json" -Raw | ConvertFrom-Json
    if ((Get-Content "$root/candidate.json" -Raw).Contains($env:GH_TOKEN)) { throw 'Token leaked into candidate receipt.' }
    if ($receipt.version -cne '7.7.0-preview.10' -or $receipt.status -ne 'resolved-only' -or $receipt.promoted) {
        throw 'Exact semantic preview selection or qualification boundary failed.'
    }
    foreach ($case in @('none', 'digest', 'url', 'duplicate', 'draft')) {
        $release = New-Release '7.7.0-preview.10'
        switch ($case) {
            'none' { $global:FinancePreviewMock = @() }
            'digest' { $release.assets[0].digest = ''; $global:FinancePreviewMock = @($release) }
            'url' { $release.assets[0].browser_download_url = 'https://example.invalid/archive.zip'; $global:FinancePreviewMock = @($release) }
            'duplicate' { $release.assets = @($release.assets[0], $release.assets[0]); $global:FinancePreviewMock = @($release) }
            'draft' { $release.draft = $true; $global:FinancePreviewMock = @($release) }
        }
        $refused = $false
        try { & "$PSScriptRoot/Resolve-PowerShellPreview.ps1" -OutputDirectory $root -ResolveOnly } catch { $refused = $true }
        $receipt = Get-Content "$root/candidate.json" -Raw | ConvertFrom-Json
        if (-not $refused -or $receipt.status -ne 'discovery-or-runtime-failed') { throw "Failed to refuse $case candidate." }
    }
    $global:FinancePreviewMock = @((New-Release '7.7.0-preview.10'))
    $refused = $false
    try { & "$PSScriptRoot/Resolve-PowerShellPreview.ps1" -OutputDirectory $root } catch {
        if ($_.Exception.Message -notmatch 'SHA256 mismatch') { throw }
        $refused = $true
    }
    if (-not $refused -or (Test-Path "$root/runtime")) { throw 'Damaged archive was not refused before extraction.' }
    Write-Host 'PowerShell preview resolver: seven selection/integrity/refusal cases passed.'
} finally { $env:GH_TOKEN = $savedToken; Remove-Variable FinancePreviewHeaders -Scope Global; Remove-Variable FinancePreviewMock -Scope Global; if (Test-Path $root) { Remove-Item -LiteralPath $root -Recurse -Force } }
