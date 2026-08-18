[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$profileFiles = @(
    Get-ChildItem -Path (Join-Path $RepositoryRoot 'copilot'), (Join-Path $RepositoryRoot 'scout') -Recurse -File
)
$patterns = @(
    '(?i)^\s*(?:api[_-]?key|authorization|credential|password|secret|token|client[_-]?secret)\s*:',
    'ghp_[A-Za-z0-9]{20,}',
    'github_pat_[A-Za-z0-9_]{20,}',
    'sk-[A-Za-z0-9_-]{20,}',
    'AKIA[0-9A-Z]{16}',
    '-----BEGIN [A-Z ]*PRIVATE KEY-----',
    '(?i)bearer\s+[A-Za-z0-9._-]{16,}',
    '(?i)accountkey\s*='
)

$findings = @()
foreach ($file in $profileFiles) {
    $content = Get-Content -Raw -LiteralPath $file.FullName
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            $findings += "$($file.FullName): matched '$pattern'."
        }
    }
}

Get-Content -Raw -LiteralPath (Join-Path $RepositoryRoot 'scout\m-settings.example.json') |
    ConvertFrom-Json |
    Out-Null

if ($findings) {
    $findings | Sort-Object -Unique | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "Validated public Copilot and Scout profiles: $($profileFiles.Count) file(s)."
