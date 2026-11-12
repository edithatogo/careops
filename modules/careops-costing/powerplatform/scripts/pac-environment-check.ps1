# Read-only access check for one explicit Dataverse target using an existing session.
param(
    [switch]$Verbose,
    [string]$EnvironmentName = 'Development',
    [string]$EnvironmentUrl = '',
    [string]$PacPath = ''
)

$ErrorActionPreference = 'Stop'
try {
    $target = $null
    if (-not [Uri]::TryCreate($EnvironmentUrl, [UriKind]::Absolute, [ref]$target) -or
        $target.Scheme -ne 'https' -or $target.UserInfo -or $target.Query -or
        $target.Fragment -or $target.AbsolutePath -ne '/') {
        throw 'Supply the exact HTTPS Dataverse environment root with -EnvironmentUrl. No active-environment fallback is used.'
    }
    if ($PacPath) {
        if (-not (Test-Path -LiteralPath $PacPath -PathType Leaf)) {
            throw 'The explicitly selected PAC executable does not exist.'
        }
        $pacExecutable = (Resolve-Path -LiteralPath $PacPath).Path
    } else {
        $pacExecutable = (Get-Command pac -CommandType Application -ErrorAction Stop).Source
    }
    # Do not create/select auth profiles, enumerate tenant environments or retry
    # a denial. The caller selects its already-qualified executable and session.
    $result = & $pacExecutable org who --environment $target.AbsoluteUri 2>&1
    if ($LASTEXITCODE -ne 0 -or -not ($result | Out-String).Trim()) {
        if ($Verbose) { Write-Host ($result | Out-String) }
        throw 'The exact-target identity/access read failed or returned no evidence. Preserve the current profile and reconcile its account, tenant and supported VS Code route; no login was attempted.'
    }
    if ($Verbose) { Write-Host ($result | Out-String) }
    Write-Host "Exact-target identity/access read succeeded: $EnvironmentName ($($target.AbsoluteUri))"
    Write-Host 'Inspect the returned identity against the intended account/tenant before deployment. This check grants no deployment authority and proves no solution membership or runtime behaviour.'
} catch {
    Write-Host "Environment check failed: $($_.Exception.Message)"
    exit 1
}
