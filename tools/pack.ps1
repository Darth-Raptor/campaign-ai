param(
    [string]$OutputRoot = ".",
    [string]$AddonBuilderPath = "",
    [string]$PboProjectPath = "",
    [string]$FileBankPath = ""
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if (!(Test-Path $OutputRoot)) {
    New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null
}
$outRoot = Resolve-Path $OutputRoot
$modRoot = Join-Path $outRoot "@Campaign_AI"
$addonsOut = Join-Path $modRoot "addons"
$addonsSrc = Join-Path $repoRoot "addons"

& (Join-Path $PSScriptRoot "build.ps1") -OutputRoot $OutputRoot
Assert-CampaignAIPythonPackage -ModRoot $modRoot

New-Item -ItemType Directory -Force -Path $addonsOut | Out-Null

$hemtt = Get-Command "hemtt" -ErrorAction SilentlyContinue
if ($hemtt) {
    Write-Host "[CAI PACK] HEMTT detected. Running hemtt build."
    Push-Location $repoRoot
    try {
        hemtt build
    }
    finally {
        Pop-Location
    }
    Write-Host "[CAI PACK] HEMTT build complete. Copy generated PBOs into $addonsOut if your HEMTT project outputs elsewhere."
    Assert-CampaignAIPythonPackage -ModRoot $modRoot
    return
}

if (-not $PboProjectPath) {
    $candidate = Get-Command "pboProject.exe" -ErrorAction SilentlyContinue
    if ($candidate) {
        $PboProjectPath = $candidate.Source
    }
}

if ($PboProjectPath -and (Test-Path $PboProjectPath)) {
    Get-ChildItem -LiteralPath $addonsSrc -Directory | ForEach-Object {
        $pboName = "cai_$($_.Name).pbo"
        Write-Host "[CAI PACK] Packing $($_.Name) with pboProject."
        & $PboProjectPath -P $_.FullName $addonsOut
        $generated = Join-Path $addonsOut "$($_.Name).pbo"
        if (Test-Path $generated) {
            Rename-Item -LiteralPath $generated -NewName $pboName -Force
        }
    }
    Assert-CampaignAIPythonPackage -ModRoot $modRoot
    return
}

if (-not $FileBankPath) {
    $defaultFileBank = "${env:ProgramFiles(x86)}\Steam\steamapps\common\Arma 3 Tools\FileBank\FileBank.exe"
    if (Test-Path $defaultFileBank) {
        $FileBankPath = $defaultFileBank
    }
}

if ($FileBankPath -and (Test-Path $FileBankPath)) {
    Get-ChildItem -LiteralPath $addonsSrc -Directory | ForEach-Object {
        $pboName = "cai_$($_.Name).pbo"
        $prefix = "x\cai\addons\$($_.Name)"
        Write-Host "[CAI PACK] Packing $($_.Name) with FileBank."
        & $FileBankPath -property "prefix=$prefix" -dst $addonsOut $_.FullName
        $generated = Join-Path $addonsOut "$($_.Name).pbo"
        $target = Join-Path $addonsOut $pboName
        if (Test-Path $generated) {
            if (Test-Path $target) {
                Remove-Item -LiteralPath $target -Force
            }
            Rename-Item -LiteralPath $generated -NewName $pboName -Force
        }
    }
    Assert-CampaignAIPythonPackage -ModRoot $modRoot
    return
}

if (-not $AddonBuilderPath) {
    $defaultAddonBuilder = "${env:ProgramFiles(x86)}\Steam\steamapps\common\Arma 3 Tools\AddonBuilder\AddonBuilder.exe"
    if (Test-Path $defaultAddonBuilder) {
        $AddonBuilderPath = $defaultAddonBuilder
    }
}

if ($AddonBuilderPath -and (Test-Path $AddonBuilderPath)) {
    Get-ChildItem -LiteralPath $addonsSrc -Directory | ForEach-Object {
        $pboName = "cai_$($_.Name).pbo"
        Write-Host "[CAI PACK] Packing $($_.Name) with AddonBuilder."
        & $AddonBuilderPath $_.FullName $addonsOut -clear
        $generated = Join-Path $addonsOut "$($_.Name).pbo"
        $target = Join-Path $addonsOut $pboName
        if (Test-Path $generated) {
            if (Test-Path $target) {
                Remove-Item -LiteralPath $target -Force
            }
            Rename-Item -LiteralPath $generated -NewName $pboName -Force
        }
    }
    Assert-CampaignAIPythonPackage -ModRoot $modRoot
    return
}

$unpackedOut = Join-Path $modRoot "addons_unpacked"
New-Item -ItemType Directory -Force -Path $unpackedOut | Out-Null
Get-ChildItem -LiteralPath $addonsSrc -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $unpackedOut -Recurse -Force
}
Assert-CampaignAIPythonPackage -ModRoot $modRoot

Write-Warning "[CAI PACK] No supported PBO packer was detected. Addon source was staged at $unpackedOut for inspection."
Write-Warning "[CAI PACK] Install HEMTT, Mikero pboProject, or Arma 3 Tools AddonBuilder to produce deployable PBOs."

