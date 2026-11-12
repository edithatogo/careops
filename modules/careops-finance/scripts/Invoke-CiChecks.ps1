[CmdletBinding()]
param(
    [ValidateSet("RepositoryHygiene", "SourceControlReady")]
    [string] $Mode = "SourceControlReady",
    [switch] $SkipPowerBiCli
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

& "$PSScriptRoot\Invoke-Validation.ps1" -Mode RepositoryHygiene -SkipPowerBiCli:$SkipPowerBiCli
& "$PSScriptRoot\Invoke-Validation.ps1" -Mode SourceControlReady -SkipPowerBiCli:$SkipPowerBiCli
Write-Host "CI gate checks completed."
