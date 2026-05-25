param(
    [ValidateSet("Phase1-Listen", "Phase2-LocalDedicated", "Phase3-HostHavoc")]
    [string]$Phase = "Phase1-Listen"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$template = Join-Path $repoRoot "qa\templates\test_log_template.md"
$logRoot = Join-Path $repoRoot "qa\logs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outPath = Join-Path $logRoot "$($Phase)_$timestamp.md"
$content = Get-Content -Raw -LiteralPath $template
$content = $content.Replace("{{PHASE}}", $Phase)
$content = $content.Replace("{{DATE_TIME}}", (Get-Date -Format s))
Set-Content -LiteralPath $outPath -Value $content -Encoding UTF8

Write-Host "[CAI TEST] Test log created: $outPath"

