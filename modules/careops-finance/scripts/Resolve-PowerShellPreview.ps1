[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $OutputDirectory,
    [switch] $ResolveOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$receiptPath = Join-Path $OutputDirectory 'candidate.json'
$receipt = [ordered]@{
    sourceCommit = $env:GITHUB_SHA
    status = 'discovery-started'
    promoted = $false
    nativeWrites = $false
}
try {
    $headers = @{ Accept = 'application/vnd.github+json' }
    if ($env:GH_TOKEN) { $headers.Authorization = "Bearer $env:GH_TOKEN" }
    $releases = Invoke-RestMethod -Headers $headers -Uri 'https://api.github.com/repos/PowerShell/PowerShell/releases?per_page=100' -TimeoutSec 30
    $release = $releases | Where-Object { $_.prerelease -and -not $_.draft -and $_.tag_name -match '^v\d+\.\d+\.\d+-preview\.\d+$' } |
        Sort-Object { [System.Management.Automation.SemanticVersion]$_.tag_name.Substring(1) } -Descending | Select-Object -First 1
    if ($null -eq $release) { throw 'No official PowerShell preview was discovered.' }
    $version = $release.tag_name.Substring(1)
    $name = "PowerShell-$version-win-x64.zip"
    $assets = @($release.assets | Where-Object { $_.name -ceq $name })
    if ($assets.Count -ne 1) { throw 'Expected exactly one Windows x64 preview archive.' }
    $asset = $assets[0]
    $expectedUrl = "https://github.com/PowerShell/PowerShell/releases/download/$($release.tag_name)/$name"
    if ($asset.browser_download_url -cne $expectedUrl -or $asset.digest -cnotmatch '^sha256:[a-f0-9]{64}$') {
        throw 'Official archive URL or published SHA256 is missing or invalid.'
    }
    $receipt.version = $version
    $receipt.url = $expectedUrl
    $receipt.sha256 = $asset.digest.Substring(7)
    $receipt.status = 'resolved-only'
    if (-not $ResolveOnly) {
        $receipt.status = 'download-started'
        $archive = Join-Path $OutputDirectory $name
        Invoke-WebRequest -Uri $expectedUrl -OutFile $archive -TimeoutSec 180
        $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -cne $receipt.sha256) { throw 'PowerShell preview archive SHA256 mismatch.' }
        $runtime = Join-Path $OutputDirectory 'runtime'
        Expand-Archive -LiteralPath $archive -DestinationPath $runtime -Force
        $exe = Join-Path $runtime 'pwsh.exe'
        if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Preview executable is missing.' }
        $reported = & $exe -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'
        if ($LASTEXITCODE -ne 0 -or $reported -cne $version) { throw 'Downloaded runtime version does not match the resolved preview.' }
        $receipt.status = 'integrity-and-runtime-verified'
        if ($env:GITHUB_OUTPUT) { "executable=$exe" | Out-File -FilePath $env:GITHUB_OUTPUT -Append -Encoding utf8 }
    }
} catch {
    $receipt.status = 'discovery-or-runtime-failed'
    throw
} finally {
    $receipt | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receiptPath -Encoding utf8
}
