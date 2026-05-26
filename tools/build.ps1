param(
    [string]$OutputRoot = "."
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
$pythonOut = Join-Path $modRoot "python_code"

Write-Host "[CAI BUILD] Staging @Campaign_AI at $modRoot"

function Remove-WithRetry {
    param(
        [string]$Path,
        [int]$Attempts = 5
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
            return
        }
        catch {
            if ($attempt -eq $Attempts) {
                throw "Unable to clean '$Path'. Close Arma/Arma Tools processes that may be using staged PBOs, or run with a different -OutputRoot. Last error: $($_.Exception.Message)"
            }
            Start-Sleep -Milliseconds (250 * $attempt)
        }
    }
}

if (Test-Path $modRoot) {
    Remove-WithRetry -Path $modRoot
}

New-Item -ItemType Directory -Force -Path $addonsOut | Out-Null
New-Item -ItemType Directory -Force -Path $pythonOut | Out-Null

$pythonSource = Join-Path $repoRoot "python_code"
if (!(Test-Path -LiteralPath $pythonSource)) {
    throw "Missing source Python package folder: $pythonSource"
}

Get-ChildItem -LiteralPath $pythonSource -Force | Where-Object { $_.Name -ne "__pycache__" } | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $pythonOut -Recurse -Force
}

Get-ChildItem -LiteralPath $pythonOut -Recurse -Force | Where-Object {
    $_.PSIsContainer -and $_.Name -eq "__pycache__"
} | Remove-Item -Recurse -Force

Get-ChildItem -LiteralPath $pythonOut -Recurse -Force | Where-Object {
    !$_.PSIsContainer -and ($_.Extension -eq ".pyc" -or $_.Extension -eq ".pyo")
} | Remove-Item -Force

Assert-CampaignAIPythonPackage -ModRoot $modRoot

$readme = Join-Path $repoRoot "README.md"
if (Test-Path $readme) {
    Copy-Item -LiteralPath $readme -Destination (Join-Path $modRoot "README.md") -Force
}

$modCpp = Join-Path $repoRoot "mod.cpp"
if (Test-Path $modCpp) {
    Copy-Item -LiteralPath $modCpp -Destination (Join-Path $modRoot "mod.cpp") -Force
}

Write-Host "[CAI BUILD] Python package staged."
Write-Host "[CAI BUILD] Run tools\pack.ps1 to create PBOs in @Campaign_AI\addons."

