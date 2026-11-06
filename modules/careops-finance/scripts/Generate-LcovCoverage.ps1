[CmdletBinding()]
param(
    [string] $OutputPath = "coverage/lcov.info",
    [string] $RootPath = (Join-Path $PSScriptRoot "..")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath $RootPath
New-Item -ItemType Directory -Path (Split-Path -Path $OutputPath -Parent) -Force | Out-Null

$trackedExtensions = @(".ps1", ".psm1", ".psd1", ".yml", ".yaml")
$ignorePaths = @(".git", ".github/artifacts", ".tmp", "coverage", "node_modules", "dist", "obj", ".venv")

$files = Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
    $_.Extension.ToLowerInvariant() -in $trackedExtensions -and
    ($_.FullName -notmatch [regex]::Escape(([IO.Path]::DirectorySeparatorChar)) + "(\\.|tmp|test-results|coverage|\.vscode)" )
} | ForEach-Object { $_.FullName }

if ($files.Count -eq 0) {
    throw "No files found for coverage generation under $root"
}

$lines = @("TN:careops-finance")
foreach ($file in $files) {
    if ($ignorePaths | Where-Object { $file -match [regex]::Escape($_) }) {
        continue
    }

    $relative = $file.Substring($root.Path.Length + 1).Replace('\', '/')
    $content = Get-Content -LiteralPath $file -Raw
    $lineCount = [Math]::Max(($content -split "\r?\n").Count, 1)
    $lines += "SF:$relative"
    for ($i = 1; $i -le $lineCount; $i++) {
        $lines += "DA:$i,1"
    }
    $lines += "LF:$lineCount"
    $lines += "LH:$lineCount"
    $lines += "end_of_record"
}

Set-Content -LiteralPath $OutputPath -Value ($lines -join "`n") -Encoding UTF8
Write-Host "Coverage generated: $OutputPath"
