[CmdletBinding()]
param(
    [string] $OutputPath = 'coverage/lcov.info',
    [string] $RootPath = (Join-Path $PSScriptRoot '..')
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $RootPath).Path
$tests = @(Get-ChildItem (Join-Path $root 'tests') -Recurse -File -Filter 'Test-*.ps1')
if ($tests.Count -eq 0) { throw 'No executable fixture tests selected.' }
$owned = @()
$records = @()
try {
    foreach ($file in @(Get-ChildItem (Join-Path $root 'scripts') -Recurse -File -Filter '*.ps1')) {
        if ($file.FullName -eq $PSCommandPath) { continue }
        $tokens = $null; $errors = $null
        $tree = [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors)
        if (@($errors).Count -ne 0) { throw 'Cannot instrument source with syntax errors.' }
        # Measure parsed executable statement start lines, never mark arbitrary
        # physical lines or unexecuted source as hit. This is not branch coverage.
        $lines = @($tree.FindAll({ param($node)
            $node -is [System.Management.Automation.Language.CommandAst] -or
            $node -is [System.Management.Automation.Language.AssignmentStatementAst] -or
            $node -is [System.Management.Automation.Language.ReturnStatementAst] -or
            $node -is [System.Management.Automation.Language.ThrowStatementAst]
        }, $true) | ForEach-Object { $_.Extent.StartLineNumber } | Sort-Object -Unique)
        foreach ($line in $lines) {
            $point = Set-PSBreakpoint -Script $file.FullName -Line $line -Action {}
            $owned += $point
            $records += [pscustomobject]@{ Path=$file.FullName; Line=$line; Point=$point }
        }
    }
    if ($records.Count -eq 0) { throw 'No executable source statements instrumented.' }
    Push-Location $root
    try { foreach ($test in $tests) { & $test.FullName } }
    finally { Pop-Location }
    $lines = @('TN:careops-finance-measured-statements')
    $totalHits = 0
    foreach ($group in @($records | Group-Object Path)) {
        $relative = [IO.Path]::GetRelativePath($root, $group.Name).Replace('\','/')
        $lines += "SF:$relative"
        $hits = 0
        foreach ($record in $group.Group) {
            $count = $record.Point.HitCount
            $lines += "DA:$($record.Line),$count"
            if ($count -gt 0) { $hits++; $totalHits++ }
        }
        $lines += "LF:$($group.Count)", "LH:$hits", 'end_of_record'
    }
    if ($totalHits -eq 0) { throw 'Tests executed no instrumented source statements.' }
    $parent = Split-Path -Parent $OutputPath
    if ($parent) { New-Item -ItemType Directory -Force $parent | Out-Null }
    Set-Content -LiteralPath $OutputPath -Value ($lines -join "`n") -Encoding UTF8
    Write-Host "Measured $totalHits/$($records.Count) executable statement lines; branch coverage is unmeasured."
} finally {
    if ($owned.Count) { $owned | Remove-PSBreakpoint }
}
