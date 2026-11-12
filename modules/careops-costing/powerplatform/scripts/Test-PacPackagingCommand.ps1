# Exercise only command selection; never invoke packaging, workers or authentication.
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$source = Join-Path $PSScriptRoot 'pac-solution-package.ps1'
$ast = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { throw 'Packaging script does not parse.' }
$definition = $ast.Find({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-PacCliCommand' }, $true)
if ($null -eq $definition) { throw 'Packaging command selector is absent.' }
$selector = [scriptblock]::Create($definition.Extent.Text)
& {
    # A legacy cached path exists, but the selected PATH executable must win.
    function Test-Path { return $true }
    function Get-Command { param($Name, $ErrorAction) return [pscustomobject]@{ Source = 'qualified-path-pac' } }
    . $selector
    if ((Get-PacCliCommand) -ne 'qualified-path-pac') { throw 'Legacy cache shadowed the selected executable.' }
}
& {
    # A legacy cache cannot silently satisfy a missing selected CLI.
    function Test-Path { return $true }
    function Get-Command { param($Name, $ErrorAction) return $null }
    . $selector
    $refused = $false
    try { $null = Get-PacCliCommand } catch { $refused = $_.Exception.Message -eq 'PAC CLI executable not found.' }
    if (-not $refused) { throw 'Missing selected CLI was not refused.' }
}
Write-Host 'PAC selection regression checks passed; no package/authentication operation executed.'
