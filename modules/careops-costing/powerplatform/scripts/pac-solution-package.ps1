# PAC CLI Solution Package Script
# Creates and packages Power Platform solution for deployment

param(
    [string]$SolutionName = "WorkforceCosting",
    [string]$PublisherPrefix = "nsw",
    [string]$OutputPath = ".\dist",
    [switch]$Managed,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Get-PacCliCommand {
    $pacCommand = Get-Command pac -ErrorAction SilentlyContinue
    if ($pacCommand) {
        return $pacCommand.Source
    }

    throw "PAC CLI executable not found."
}

function Reset-PacWorker {
    $worker = Get-Process pacjsworker -ErrorAction SilentlyContinue
    if ($worker) {
        $worker | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}

function Resolve-RepoRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return (Resolve-Path $candidate).Path
        }
    }

    return $null
}

$pacCli = Get-PacCliCommand
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PAC Solution Package" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputPath)) {
    Write-Host "Creating output directory: $OutputPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
}

# Initialize solution if not exists
$solutionProjectPath = Resolve-RepoRelativePath @(
    (Join-Path $repoRoot "solution_bootstrap")
    (Join-Path $repoRoot "solution_pac")
    (Join-Path $repoRoot "solution")
)
$solutionSourcePath = if ($solutionProjectPath) {
    Join-Path $solutionProjectPath "src"
} else {
    $null
}
if (-not (Test-Path $solutionProjectPath)) {
    Write-Host "Initializing new solution: $SolutionName" -ForegroundColor Yellow
    Reset-PacWorker
    & $pacCli solution init --publisher-prefix $PublisherPrefix --output-directory $solutionProjectPath

    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to initialize solution" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Solution initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Solution directory exists" -ForegroundColor Green
}

if (-not (Test-Path $solutionSourcePath)) {
    Write-Host "✗ Solution source directory not found: $solutionSourcePath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Pack solution
Write-Host "Packing solution..." -ForegroundColor Yellow
$zipFileName = if ($Managed) { "$SolutionName-managed.zip" } else { "$SolutionName-unmanaged.zip" }
$zipPath = Join-Path $OutputPath $zipFileName
$packageType = if ($Managed) { "Managed" } else { "Unmanaged" }

Reset-PacWorker
$packOutput = & $pacCli solution pack --zipfile $zipPath --folder $solutionSourcePath --packagetype $packageType 2>&1
$packExitCode = $LASTEXITCODE
$packOutputText = ($packOutput | Out-String).Trim()
$packReportedError = $packOutputText -match '(^|\r?\n)\s*Error:'

if ($packOutputText) {
    Write-Host $packOutputText
}

if ($packExitCode -ne 0 -or $packReportedError -or -not (Test-Path $zipPath)) {
    Write-Host "✗ Failed to pack solution" -ForegroundColor Red

    if ($packOutputText -match "Duplicate root component '00000000-0000-0000-0000-000000000000' of type 'Entity'") {
        Write-Host "  The current entity XML files are not in PAC's valid unpacked-entity format." -ForegroundColor Yellow
        Write-Host "  Next step: bootstrap from a real exported solution or exported Dataverse tables, then patch the unpacked artifacts." -ForegroundColor Yellow
    }

    if (-not (Test-Path $zipPath)) {
        Write-Host "  Expected output was not created: $zipPath" -ForegroundColor Red
    }

    exit 1
}

Write-Host "✓ Solution packed successfully: $zipFileName" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Package Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output:" -ForegroundColor White
Write-Host "  $zipPath" -ForegroundColor Gray
Write-Host ""

if ($Managed) {
    Write-Host "Note: This is a MANAGED solution." -ForegroundColor Yellow
    Write-Host "      Managed solutions cannot be unpacked after import." -ForegroundColor Gray
} else {
    Write-Host "Note: This is an UNMANAGED solution." -ForegroundColor Yellow
    Write-Host "      Use for development and testing environments." -ForegroundColor Gray
}

Write-Host ""
