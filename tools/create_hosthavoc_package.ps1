param(
    [string]$PackageName = ""
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if (-not $PackageName) {
    $PackageName = "Campaign_AI_HostHavoc_$timestamp"
}

$packageRoot = Join-Path $repoRoot "qa\packages"
$workRoot = Join-Path $packageRoot $PackageName
$zipPath = Join-Path $packageRoot "$PackageName.zip"
$buildRoot = Join-Path $repoRoot "qa\stage_builds\hosthavoc_$timestamp"

New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null

if (Test-Path $workRoot) {
    Remove-Item -LiteralPath $workRoot -Recurse -Force
}
if (Test-Path $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

& (Join-Path $PSScriptRoot "pack.ps1") -OutputRoot $buildRoot
if ($LASTEXITCODE -ne 0) {
    throw "Packaging failed."
}

New-Item -ItemType Directory -Force -Path $workRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $workRoot "MPMissions") | Out-Null

Copy-Item -LiteralPath (Join-Path $buildRoot "@Campaign_AI") -Destination (Join-Path $workRoot "@Campaign_AI") -Recurse -Force

$missionSource = Join-Path $repoRoot "missions\CAI_V1_SmokeTest.VR"
$missionTargetRoot = Join-Path $workRoot "MPMissions"
$missionPboTarget = Join-Path $missionTargetRoot "CAI_V1_SmokeTest.VR.pbo"
$fileBank = Find-CampaignAIFileBank
$missionUpload = "MPMissions\CAI_V1_SmokeTest.VR"
if ($fileBank) {
    & $fileBank -dst $missionTargetRoot $missionSource
    if (!(Test-Path -LiteralPath $missionPboTarget)) {
        throw "Mission PBO was not created: $missionPboTarget"
    }
    $missionUpload = "MPMissions\CAI_V1_SmokeTest.VR.pbo"
}
else {
    Copy-Item -LiteralPath $missionSource -Destination (Join-Path $missionTargetRoot "CAI_V1_SmokeTest.VR") -Recurse -Force
    Write-Warning "[CAI TEST] FileBank.exe not found. HostHavoc package contains unpacked mission folder instead of mission PBO."
}

Assert-CampaignAIPythonPackage -ModRoot (Join-Path $workRoot "@Campaign_AI")

$readme = @"
Campaign AI V1.0 HostHavoc Smoke-Test Package

Upload contents:
- @Campaign_AI
- $missionUpload

Also required on the server:
- @Pythia

Server startup flags:
-mod=@Pythia;@Campaign_AI -autoInit

Primary validation doc:
docs/testing/three_phase_test_plan.md

Expected RPT lines:
[CAI CORE] Campaign AI core initialized.
[CAI PYTHIA] Ping successful. Package: CAIPython.
[CAI MODULE] Initial Pythia save/load proof path completed.
"@

Set-Content -LiteralPath (Join-Path $workRoot "HOSTHAVOC_README.txt") -Value $readme -Encoding UTF8

Compress-Archive -Path (Join-Path $workRoot "*") -DestinationPath $zipPath -Force

Write-Host "[CAI TEST] HostHavoc package created: $zipPath"
