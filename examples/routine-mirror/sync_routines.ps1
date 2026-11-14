<#
.SYNOPSIS
  Mirror routine scripts into a Git clone, scan them, and commit + push only if something changed.
.PARAMETER Config   Path to routines.json (see routines.example.json).
.PARAMETER Mirror   Path to a local clone of the mirror repo.
.PARAMETER NoPush   Commit locally but do not push.
#>
param(
    [string]$Config = (Join-Path $PSScriptRoot "routines.json"),
    [Parameter(Mandatory = $true)][string]$Mirror,
    [switch]$NoPush
)
$ErrorActionPreference = "Stop"
$scan = Join-Path $PSScriptRoot "secret_scan.py"
$cfg = Get-Content $Config -Raw | ConvertFrom-Json

foreach ($r in $cfg.routines) {
    # Rule 1: skip (never delete) when a source is missing.
    $missing = @($r.sources | Where-Object { -not (Test-Path $_) })
    if ($missing.Count -gt 0) {
        Write-Warning "SKIP $($r.name): missing $($missing -join ', ')"
        continue
    }
    $dest = Join-Path $Mirror "routines\$($r.name)"
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    New-Item -ItemType Directory -Path $dest -Force | Out-Null

    foreach ($s in $r.sources) {
        if (Test-Path $s -PathType Container) {
            $base = (Resolve-Path $s).Path
            Get-ChildItem $s -Recurse -File -Include $r.include | ForEach-Object {
                $rel = $_.FullName.Substring($base.Length).TrimStart('\')
                $target = Join-Path $dest $rel
                New-Item -ItemType Directory -Path (Split-Path $target) -Force | Out-Null
                Copy-Item $_.FullName $target
            }
        }
        else {
            Copy-Item $s $dest
        }
    }
    $desc = Join-Path $dest "README.md"
    if (-not (Test-Path $desc)) { Set-Content -Path $desc -Value "# $($r.name)`n`n$($r.description)" -Encoding UTF8 }
}

# Rule 2: scan before committing; a failed scan stops everything.
& python $scan $Mirror
if ($LASTEXITCODE -ne 0) { throw "Secret scan failed; nothing was committed." }

Push-Location $Mirror
try {
    git add -A
    if (-not (git status --porcelain)) { "No changes."; return }
    git commit -q -m "Sync routines $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    if (-not $NoPush -and (git remote)) {
        git push -q
        if ($LASTEXITCODE -ne 0) { throw "git push failed; check the remote." }
    }
    "Committed."
}
finally { Pop-Location }
