param(
    [string]$TargetRoot = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Server",
    [switch]$SkipPack
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$targetRootPath = Resolve-Path $TargetRoot
$missionSource = Join-Path $repoRoot "missions\CAI_V1_SmokeTest.VR"
$missionTargetRoot = Join-Path $targetRootPath "MPMissions"
$missionTarget = Join-Path $missionTargetRoot "CAI_V1_SmokeTest.VR"
$missionPboTarget = Join-Path $missionTargetRoot "CAI_V1_SmokeTest.VR.pbo"
$stageTimestamp = "$(Get-Date -Format "yyyyMMdd_HHmmss")_$(([guid]::NewGuid().ToString("N")).Substring(0, 8))"
$stageBuildRoot = Join-Path $repoRoot "qa\stage_builds\$stageTimestamp"
$modSource = Join-Path $stageBuildRoot "@Campaign_AI"
$modTarget = Join-Path $targetRootPath "@Campaign_AI"

if (-not $SkipPack) {
    & (Join-Path $PSScriptRoot "pack.ps1") -OutputRoot $stageBuildRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Packaging failed."
    }
}
else {
    $modSource = Join-Path $repoRoot "@Campaign_AI"
}

if (!(Test-Path $modSource)) {
    throw "Staged @Campaign_AI not found. Run tools\pack.ps1 first."
}

Assert-CampaignAIPythonPackage -ModRoot $modSource

New-Item -ItemType Directory -Force -Path $missionTargetRoot | Out-Null

if (Test-Path $missionTarget) {
    Remove-Item -LiteralPath $missionTarget -Recurse -Force
}
if (Test-Path $missionPboTarget) {
    Remove-Item -LiteralPath $missionPboTarget -Force
}
Copy-Item -LiteralPath $missionSource -Destination $missionTarget -Recurse -Force

$fileBank = Find-CampaignAIFileBank
if ($fileBank) {
    & $fileBank -dst $missionTargetRoot $missionSource
    if (!(Test-Path -LiteralPath $missionPboTarget)) {
        throw "Mission PBO was not created: $missionPboTarget"
    }
    Write-Host "[CAI TEST] Staged mission PBO: $missionPboTarget"
}
else {
    Write-Warning "[CAI TEST] FileBank.exe not found. Staged unpacked mission folder only."
}

if (Test-Path $modTarget) {
    Remove-Item -LiteralPath $modTarget -Recurse -Force
}
Copy-Item -LiteralPath $modSource -Destination $modTarget -Recurse -Force

Write-Host "[CAI TEST] Staged mission: $missionTarget"
Write-Host "[CAI TEST] Staged mod: $modTarget"
Write-Host "[CAI TEST] Ensure @Pythia is also installed at $targetRootPath\@Pythia"
