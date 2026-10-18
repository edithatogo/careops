[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [switch]$IncludeCareOpsApprove,
    [string]$TargetsPath
)

$ErrorActionPreference = 'Stop'

# Supply enterprise targets through an untracked private configuration file.
$targets = @(@{ Host = 'github.com'; Repo = 'edithatogo/careops' })
if ($TargetsPath) {
    $targets = @(Get-Content -Raw -LiteralPath $TargetsPath | ConvertFrom-Json)
    if ($targets.Count -eq 0) { throw 'At least one explicit target is required.' }
    foreach ($target in $targets) {
        if ($target.Host -notmatch '^[A-Za-z0-9.-]+$' -or
            $target.Repo -notmatch '^[A-Za-z0-9_.-]+/careops$') {
            throw 'Invalid issue-sync target; expected a host and owner/careops.'
        }
    }
}

function Invoke-GhJson {
    param([string]$HostName, [string[]]$Arguments)
    $output = & gh @Arguments --hostname $HostName 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($output -join "`n") }
    if (-not $output) { return $null }
    return ($output -join "`n") | ConvertFrom-Json
}

function Ensure-Label {
    param($Target, [string]$Name, [string]$Color, [string]$Description)
    $encoded = [uri]::EscapeDataString($Name)
    try {
        Invoke-GhJson $Target.Host @('api', "repos/$($Target.Repo)/labels/$encoded") | Out-Null
    } catch {
        if ($PSCmdlet.ShouldProcess("$($Target.Host)/$($Target.Repo)", "create label $Name")) {
            Invoke-GhJson $Target.Host @('api', '--method', 'POST', "repos/$($Target.Repo)/labels", '-f', "name=$Name", '-f', "color=$Color", '-f', "description=$Description") | Out-Null
        }
    }
}

function Get-ExistingIssues {
    param($Target)
    $pages = Invoke-GhJson $Target.Host @('api', '--paginate', '--slurp', "repos/$($Target.Repo)/issues?state=all&per_page=100")
    $items = @($pages | ForEach-Object { $_ })
    $map = @{}
    foreach ($item in @($items)) {
        if (-not $item.pull_request -and $item.body -match '<!-- conductor-track:([^>]+) -->') {
            $map[$Matches[1]] = $item
        }
    }
    return $map
}

function Sync-Track {
    param($Target, [hashtable]$Existing, [string]$Track, [string]$Lifecycle, [string]$Repository)
    $marker = "<!-- conductor-track:$Track -->"
    $closed = $Lifecycle -in @('archived', 'completed')
    $title = "Conductor: $Track"
    $body = @"
$marker

Repository: ``$Repository``
Conductor track: ``$Track``
Lifecycle: **$Lifecycle**

This issue is a sanitized traceability record. Historical evidence remains local and is deliberately not copied because it may contain operational or sensitive information.
"@
    $labels = if ($closed) { 'conductor,historical,archived' } else { 'conductor,active' }
    $issue = $Existing[$Track]
    if (-not $issue) {
        if ($PSCmdlet.ShouldProcess("$($Target.Host)/$($Target.Repo)", "create $title")) {
            $arguments = @('api', '--method', 'POST', "repos/$($Target.Repo)/issues", '-f', "title=$title", '-f', "body=$body")
            foreach ($label in $labels -split ',') { $arguments += @('-f', "labels[]=$label") }
            $issue = Invoke-GhJson $Target.Host $arguments
            $Existing[$Track] = $issue
        }
    }
    if ($issue -and $issue.body -ne $body) {
        if ($PSCmdlet.ShouldProcess("$($Target.Host)/$($Target.Repo)#$($issue.number)", "update lifecycle to $Lifecycle")) {
            Invoke-GhJson $Target.Host @('api', '--method', 'PATCH', "repos/$($Target.Repo)/issues/$($issue.number)", '-f', "body=$body") | Out-Null
        }
    }
    if ($issue -and $closed -and $issue.state -ne 'closed') {
        if ($PSCmdlet.ShouldProcess("$($Target.Host)/$($Target.Repo)#$($issue.number)", 'close archived track')) {
            Invoke-GhJson $Target.Host @('api', '--method', 'PATCH', "repos/$($Target.Repo)/issues/$($issue.number)", '-f', 'state=closed', '-f', 'state_reason=completed') | Out-Null
        }
    }
}

$labelDefinitions = @(
    @('conductor', '1d76db', 'Conductor traceability'),
    @('historical', 'bfd4f2', 'Historical work record'),
    @('archived', '6f42c1', 'Completed and archived'),
    @('active', '0e8a16', 'Current work')
)

$activePath = Join-Path $Root 'conductor/tracks'
$archivePath = Join-Path $Root 'conductor/archive'
$excluded = @('archive', 'deployment-scripts')
$active = @(Get-ChildItem $activePath -Directory | Where-Object Name -NotIn $excluded | Select-Object -ExpandProperty Name)
$archived = if (Test-Path $archivePath) { @(Get-ChildItem $archivePath -Directory | Select-Object -ExpandProperty Name) } else { @() }
$all = @($active + $archived | Sort-Object -Unique)

function Get-Lifecycle {
    param([string]$Track)
    if ($Track -in $archived) { return 'archived' }
    $trackPath = Join-Path $activePath $Track
    $metadataPath = Join-Path $trackPath 'metadata.json'
    if (Test-Path $metadataPath) {
        $metadata = Get-Content $metadataPath -Raw | ConvertFrom-Json
        if ($metadata.status -in @('complete', 'completed')) { return 'completed' }
    }
    $planPath = Join-Path $trackPath 'plan.md'
    if (Test-Path $planPath) {
        $plan = Get-Content $planPath -Raw
        if ($plan -notmatch '\[ \]' -and $plan -notmatch '\[~\]') { return 'completed' }
    }
    return 'active'
}

foreach ($target in $targets) {
    foreach ($label in $labelDefinitions) { Ensure-Label $target $label[0] $label[1] $label[2] }
    $existing = Get-ExistingIssues $target
    foreach ($track in $all) { Sync-Track $target $existing $track (Get-Lifecycle $track) 'careops' }
}

if ($IncludeCareOpsApprove) {
    $approveTargets = @($targets | ForEach-Object {
        @{ Host = $_.Host; Repo = "$($_.Repo)-approve" }
    })
    foreach ($target in $approveTargets) {
        foreach ($label in $labelDefinitions) { Ensure-Label $target $label[0] $label[1] $label[2] }
        $existing = Get-ExistingIssues $target
        $approvePath = Join-Path $Root 'careops-approve/conductor/tracks'
        $approveTracks = Get-ChildItem $approvePath -Directory
        foreach ($trackDirectory in $approveTracks) {
            $trackPath = $trackDirectory.FullName
            $lifecycle = 'active'
            $metadataPath = Join-Path $trackPath 'metadata.json'
            if (Test-Path $metadataPath) {
                $metadata = Get-Content $metadataPath -Raw | ConvertFrom-Json
                if ($metadata.status -in @('complete', 'completed')) { $lifecycle = 'completed' }
            }
            $planPath = Join-Path $trackPath 'plan.md'
            if ($lifecycle -eq 'active' -and (Test-Path $planPath)) {
                $plan = Get-Content $planPath -Raw
                if ($plan -notmatch '\[ \]' -and $plan -notmatch '\[~\]') { $lifecycle = 'completed' }
            }
            Sync-Track $target $existing $trackDirectory.Name $lifecycle 'careops-approve'
        }
    }
}

Write-Host "Synchronized $($all.Count) CareOps track records across $($targets.Count) configured target(s)."
