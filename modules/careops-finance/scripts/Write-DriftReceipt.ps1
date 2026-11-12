[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string] $Mode = "Unknown",
    [Parameter(Mandatory = $false)]
    [string] $OutputPath = "drift-receipt.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Push-Location $root
try {
    $repoUrl = git config --get remote.origin.url
    $status = @(git status --short)
    $commit = git rev-parse HEAD
    $branch = git rev-parse --abbrev-ref HEAD
    $dirty = $status | ForEach-Object { $_.Trim() }

    $receipt = [ordered]@{
        repo   = "edithatogo/careops-finance-public"
        mode   = $Mode
        branch = $branch
        commit = $commit
        actor  = (Get-Item Env:GITHUB_ACTOR -ErrorAction SilentlyContinue).Value
        ref    = (Get-Item Env:GITHUB_REF -ErrorAction SilentlyContinue).Value
        runId  = (Get-Item Env:GITHUB_RUN_ID -ErrorAction SilentlyContinue).Value
        event  = (Get-Item Env:GITHUB_EVENT_NAME -ErrorAction SilentlyContinue).Value
        remote = $repoUrl
        timeUtc = [DateTime]::UtcNow.ToString("o")
        dirtyCount = $status.Count
        dirtyPaths = $status
    }

    $receipt | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Host "Drift receipt written: $OutputPath"
}
finally {
    Pop-Location
}
