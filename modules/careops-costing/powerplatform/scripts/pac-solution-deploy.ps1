# PAC CLI Solution Deploy Script
# Deploys Power Platform solution to target environment

param(
    [string]$SolutionPath = ".\dist\WorkforceCosting-unmanaged.zip",
    [string]$EnvironmentName = "Development",
    [string]$EnvironmentUrl = "",
    [string]$PacPath = "",
    [string]$TenantId = "",
    [string]$ApplicationId = "",
    [string]$ClientSecret = "",
    [switch]$UseGithubFederated,
    [switch]$ActivatePlugins,
    [switch]$OverwriteUnmanagedCustomizations,
    [switch]$SkipDependencyCheck,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Get-PacCliCommand {
    if ($PacPath) {
        if (-not (Test-Path -LiteralPath $PacPath -PathType Leaf)) {
            throw "The explicitly selected PAC executable does not exist."
        }
        return (Resolve-Path -LiteralPath $PacPath).Path
    }
    $pacCommand = Get-Command pac -CommandType Application -ErrorAction SilentlyContinue
    if ($pacCommand) {
        return $pacCommand.Source
    }

    throw "PAC CLI executable not found."
}

function Resolve-RepoRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path (Split-Path -Parent $PSScriptRoot) $Path)
}

# Refuse ambient-target deployment before any authentication or native command.
$target = $null
if (-not [Uri]::TryCreate($EnvironmentUrl, [UriKind]::Absolute, [ref]$target) -or
    $target.Scheme -ne 'https' -or $target.UserInfo -or $target.Query -or
    $target.Fragment -or $target.AbsolutePath -ne '/') {
    throw 'Supply the exact HTTPS Dataverse environment root with -EnvironmentUrl; active-environment fallback is disabled.'
}
$EnvironmentUrl = $target.AbsoluteUri
if (($UseGithubFederated -and $ClientSecret) -or
    (($TenantId -or $ApplicationId) -and -not ($UseGithubFederated -or $ClientSecret))) {
    throw 'Select one explicit application authentication mode, or omit auth parameters to reuse the existing qualified session.'
}
$pacCli = Get-PacCliCommand
$resolvedSolutionPath = Resolve-RepoRelativePath $SolutionPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PAC Solution Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify solution file exists
if (-not (Test-Path $resolvedSolutionPath)) {
    Write-Host "✗ Solution file not found: $resolvedSolutionPath" -ForegroundColor Red
    Write-Host "  Run pac-solution-package.ps1 first" -ForegroundColor Gray
    exit 1
}

Write-Host "Solution: $resolvedSolutionPath" -ForegroundColor White
Write-Host "Target Environment: $EnvironmentName" -ForegroundColor White
if ($EnvironmentUrl) {
    Write-Host "Environment URL: $EnvironmentUrl" -ForegroundColor White
}
Write-Host ""

if ($UseGithubFederated -or $ClientSecret) {
    Write-Host "Preparing explicitly selected application auth..." -ForegroundColor Yellow
    $authArgs = @("auth", "create", "--name", "careops-ci", "--environment", $EnvironmentUrl)
    if ($UseGithubFederated) {
        if (-not $TenantId -or -not $ApplicationId) {
            throw "GitHub federated auth requires -TenantId and -ApplicationId."
        }
        $authArgs += @("--githubFederated", "--tenant", $TenantId, "--applicationId", $ApplicationId)
    } elseif ($ClientSecret) {
        if (-not $TenantId -or -not $ApplicationId) {
            throw "Client secret auth requires -TenantId and -ApplicationId."
        }
        $authArgs += @("--tenant", $TenantId, "--applicationId", $ApplicationId, "--clientSecret", $ClientSecret)
    } else {
        throw "Provide either -UseGithubFederated with tenant/application ID or -ClientSecret with tenant/application ID."
    }

    $authOutput = & $pacCli @authArgs 2>&1
    $authExitCode = $LASTEXITCODE
    $authText = ($authOutput | Out-String).Trim()
    if ($authText) {
        Write-Host $authText
    }
    if ($authExitCode -ne 0) {
        Write-Host "✗ PAC authentication failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ PAC auth profile created" -ForegroundColor Green
    Write-Host ""
}

# Check current environment
Write-Host "Verifying current environment..." -ForegroundColor Yellow
$whoArgs = @("org", "who")
if ($EnvironmentUrl) {
    $whoArgs += @("--environment", $EnvironmentUrl)
}
$orgWho = & $pacCli @whoArgs 2>&1
if ($LASTEXITCODE -ne 0 -or -not ($orgWho | Out-String).Trim()) {
    Write-Host "✗ Exact-target identity/access read failed" -ForegroundColor Red
    Write-Host "  Preserve the current profile; reconcile its intended account, tenant and qualified VS Code route before import." -ForegroundColor Gray
    exit 1
}
Write-Host "✓ Connected to environment" -ForegroundColor Green
Write-Host ""

# Build import command
$importArgs = @("solution", "import", "--path", $resolvedSolutionPath)
if ($EnvironmentUrl) {
    $importArgs += @("--environment", $EnvironmentUrl)
}

if ($ActivatePlugins) {
    $importArgs += "--activate-plugins"
}

if ($OverwriteUnmanagedCustomizations) {
    $importArgs += "--force-overwrite"
}

if ($SkipDependencyCheck) {
    $importArgs += "--skip-dependency-check"
}

if ($Verbose) {
    Write-Host "Verbose logging requested; PAC solution import does not support --verbose on this CLI build." -ForegroundColor Yellow
}

# Import solution
Write-Host "Importing solution..." -ForegroundColor Yellow
Write-Host "Command: $pacCli $($importArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

$importOutput = & $pacCli @importArgs 2>&1
$importExitCode = $LASTEXITCODE
$importText = ($importOutput | Out-String).Trim()
if ($importText) {
    Write-Host $importText
}

if ($importExitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Deployment Complete" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✓ Solution imported successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "  1. Verify solution in Power Apps portal" -ForegroundColor Gray
    Write-Host "  2. Test Canvas app functionality" -ForegroundColor Gray
    Write-Host "  3. Validate Dataverse entities" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Deployment Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "✗ Import failed with exit code: $importExitCode" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor White
    Write-Host "  - Check solution dependencies" -ForegroundColor Gray
    Write-Host "  - Verify environment permissions" -ForegroundColor Gray
    Write-Host "  - Review PAC output above for Dataverse validation errors" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
