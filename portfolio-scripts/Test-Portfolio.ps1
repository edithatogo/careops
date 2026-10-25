[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$required = @(
    'README.md', 'SECURITY.md', '.gitmodules', 'portfolio/repos.json',
    'conductor/index.md', 'conductor/product.md', 'conductor/tech-stack.md',
    'conductor/workflow.md', 'conductor/tracks.md'
)
foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $path) -PathType Leaf)) {
        throw "Missing portfolio file: $path"
    }
}

$tracked = @(git -C $root ls-files)
if ($LASTEXITCODE -ne 0) { throw 'Unable to enumerate tracked files.' }
foreach ($prefix in @('_scratch/', 'outputs/', 'contracts/', 'logs/', 'careops-system/', 'conductor/archive/')) {
    if ($tracked | Where-Object { $_ -like "$prefix*" }) {
        throw "Confidential or generated workspace path is tracked: $prefix"
    }
}

$forbiddenContent = '(?i)(client[_ -]?secret|password\s*[:=]|gh[pousr]_[A-Za-z0-9]{20,}|patient\s*(name|id|mrn)|medical\s*record\s*(number|id))'
foreach ($file in $tracked) {
    $full = Join-Path $root $file
    if ((Test-Path -LiteralPath $full -PathType Leaf) -and (Get-Content -Raw -LiteralPath $full -ErrorAction SilentlyContinue) -match $forbiddenContent) {
        throw "Potential confidential or secret content found in tracked file: $file"
    }
}

$topology = Get-Content -Raw -LiteralPath (Join-Path $root 'portfolio/repos.json') | ConvertFrom-Json
if ($topology.authority -ne 'deployment-profile' -or $topology.continuityMirror -ne 'github.com') {
    throw 'Public source topology must retain profile-supplied deployment authority and the GitHub source mirror.'
}

# Composition pins select qualified public source, not native deployment state.
$alm = Get-Content -Raw -LiteralPath (Join-Path $root 'portfolio/power-platform-alm.json') | ConvertFrom-Json
$publicInventory = Get-Content -Raw -LiteralPath (Join-Path $root 'PUBLIC_SOURCE_FILES.json') | ConvertFrom-Json
foreach ($component in $topology.components) {
    if (-not $component.publicSourceCommit) { continue }
    $records = @($alm.modules | Where-Object { $_.module -eq $component.name })
    if ($component.publicSourceCommit -cnotmatch '^[0-9a-f]{40}$') {
        throw "Composition pin does not match qualified public source: $($component.name)"
    }
    if ($component.sourceQualification -eq 'independent-rust-source') {
        $inventoryPin = $publicInventory.gitlinks.PSObject.Properties[$component.path]
        if ($records.Count -ne 0 -or -not $inventoryPin -or
            $inventoryPin.Value -cne $component.publicSourceCommit) {
            throw "Composition pin does not match qualified public source: $($component.name)"
        }
    } elseif ($records.Count -ne 1 -or
        $records[0].sourceScope -ne 'qualified-merged-public-source' -or
        $records[0].sourceCommit -cne $component.publicSourceCommit) {
        throw "Composition pin does not match qualified public source: $($component.name)"
    }
    if ($component.materialization -eq 'submodule') {
        $entry = @(git -C $root ls-files --stage -- $component.path)
        if ($LASTEXITCODE -ne 0 -or $entry.Count -ne 1 -or
            $entry[0] -cnotmatch '^160000 ([0-9a-f]{40}) 0\t(.+)$' -or
            $Matches[1] -cne $component.publicSourceCommit -or
            $Matches[2] -cne $component.path) {
            throw "Composition gitlink does not match qualified public source: $($component.name)"
        }
    }
}

Write-Output 'Portfolio validation passed.'
