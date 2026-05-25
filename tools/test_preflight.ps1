param(
    [string]$PythonExe = "",
    [switch]$SkipPack
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "common.ps1")

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$logRoot = Join-Path $repoRoot "qa\logs"
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $logRoot "preflight_$timestamp.md"
$preflightOutputRoot = Join-Path $repoRoot "qa\preflight_builds\$timestamp"
$lines = New-Object System.Collections.Generic.List[string]

function Add-Log {
    param([string]$Line)
    $lines.Add($Line)
    Write-Host $Line
}

function Resolve-Python {
    function Test-PythonCandidate {
        param([string]$Path)
        if (-not $Path) {
            return $false
        }
        try {
            & $Path --version *> $null
            return $LASTEXITCODE -eq 0
        }
        catch {
            return $false
        }
    }

    if ($PythonExe -and (Test-Path $PythonExe)) {
        $resolved = (Resolve-Path $PythonExe).Path
        if (Test-PythonCandidate $resolved) {
            return $resolved
        }
        throw "Provided Python executable did not run successfully: $resolved"
    }

    $cmd = Get-Command "python" -ErrorAction SilentlyContinue
    if ($cmd -and (Test-PythonCandidate $cmd.Source)) {
        return $cmd.Source
    }

    $codexPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if ((Test-Path $codexPython) -and (Test-PythonCandidate $codexPython)) {
        return $codexPython
    }

    throw "No Python executable found. Pass -PythonExe or install Python."
}

function Find-BankRev {
    $defaultBankRev = "${env:ProgramFiles(x86)}\Steam\steamapps\common\Arma 3 Tools\BankRev\BankRev.exe"
    if (Test-Path $defaultBankRev) {
        return $defaultBankRev
    }
    $cmd = Get-Command "BankRev.exe" -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    return ""
}

Add-Log "# Campaign AI V1.0 Preflight"
Add-Log ""
Add-Log "- Date/time: $(Get-Date -Format s)"
Add-Log "- Repo: $repoRoot"
Add-Log "- Output root: $preflightOutputRoot"
Add-Log ""

$python = Resolve-Python
Add-Log "## Python Tests"
Add-Log ""
Add-Log "- Python: $python"
& $python -m unittest discover -s tests
if ($LASTEXITCODE -ne 0) {
    throw "Python tests failed."
}
Add-Log "- Result: PASS"
Add-Log ""

if (-not $SkipPack) {
    Add-Log "## Packaging"
    Add-Log ""
    & (Join-Path $PSScriptRoot "pack.ps1") -OutputRoot $preflightOutputRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Packaging failed."
    }
    Add-Log "- Result: PASS"
    Add-Log ""
}

$modRoot = Join-Path $preflightOutputRoot "@Campaign_AI"
if ($SkipPack) {
    $modRoot = Join-Path $repoRoot "@Campaign_AI"
}

Add-Log "## Python Package Verification"
Add-Log ""
Assert-CampaignAIPythonPackage -ModRoot $modRoot
Add-Log "- Result: PASS"
Add-Log ""

$expectedPbos = @(
    "cai_core.pbo",
    "cai_pythia.pbo",
    "cai_objectives.pbo",
    "cai_virtual.pbo",
    "cai_intel.pbo",
    "cai_combat.pbo",
    "cai_commanders.pbo",
    "cai_modules.pbo"
)

$addonsPath = Join-Path $preflightOutputRoot "@Campaign_AI\addons"
if ($SkipPack) {
    $addonsPath = Join-Path $repoRoot "@Campaign_AI\addons"
}
Add-Log "## PBO Verification"
Add-Log ""
foreach ($pbo in $expectedPbos) {
    $path = Join-Path $addonsPath $pbo
    if (!(Test-Path $path)) {
        throw "Missing expected PBO: $pbo"
    }
    $length = (Get-Item $path).Length
    Add-Log "- PASS: $pbo ($length bytes)"
}
Add-Log ""

$bankRev = Find-BankRev
if ($bankRev) {
    Add-Log "## PBO Prefix Spot Checks"
    Add-Log ""
    $spotChecks = @(
        @{ Pbo = "cai_core.pbo"; Prefix = "x\cai\addons\core"; Function = "fn_initcore.sqf" },
        @{ Pbo = "cai_modules.pbo"; Prefix = "x\cai\addons\modules"; Function = "fn_initmodules.sqf" },
        @{ Pbo = "cai_combat.pbo"; Prefix = "x\cai\addons\combat"; Function = "fn_requestcombatresolution.sqf" }
    )
    foreach ($check in $spotChecks) {
        $pboPath = Join-Path $addonsPath $check.Pbo
        $props = & $bankRev -properties $pboPath
        $listing = & $bankRev -lf $pboPath
        if (($props -join "`n") -notmatch [regex]::Escape($check.Prefix)) {
            throw "PBO prefix check failed for $($check.Pbo)."
        }
        if (($listing -join "`n") -notmatch [regex]::Escape($check.Function)) {
            throw "PBO function listing check failed for $($check.Pbo)."
        }
        Add-Log "- PASS: $($check.Pbo) prefix/function contents verified"
    }
    Add-Log ""
}
else {
    Add-Log "## PBO Prefix Spot Checks"
    Add-Log ""
    Add-Log "- SKIP: BankRev.exe not found."
    Add-Log ""
}

Add-Log "## Result"
Add-Log ""
Add-Log "PASS"

Set-Content -LiteralPath $logPath -Value $lines -Encoding UTF8
Write-Host "[CAI TEST] Preflight log written to $logPath"
