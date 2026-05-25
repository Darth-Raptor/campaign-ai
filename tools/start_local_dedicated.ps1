param(
    [string]$ServerRoot = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Server",
    [string]$ServerExe = "",
    [int]$Port = 2302,
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$serverRootPath = Resolve-Path $ServerRoot

if (-not $ServerExe) {
    $candidate = Join-Path $serverRootPath "arma3server_x64.exe"
    if (!(Test-Path $candidate)) {
        $candidate = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3\arma3server_x64.exe"
    }
    $ServerExe = $candidate
}

if (!(Test-Path $ServerExe)) {
    throw "Arma 3 dedicated server executable not found: $ServerExe"
}

& (Join-Path $PSScriptRoot "stage_test_assets.ps1") -TargetRoot $serverRootPath
if ($LASTEXITCODE -ne 0) {
    throw "Test asset staging failed."
}

$config = Join-Path $repoRoot "test_servers\local_dedicated\server.cfg"
$profileRoot = Join-Path $repoRoot "qa\local_dedicated_profile"
New-Item -ItemType Directory -Force -Path $profileRoot | Out-Null

$args = @(
    "-port=$Port",
    "-config=`"$config`"",
    "-profiles=`"$profileRoot`"",
    "-name=server",
    "-mod=@Pythia;@Campaign_AI",
    "-world=empty",
    "-noSound",
    "-netlog",
    "-autoInit"
)

Write-Host "[CAI TEST] Server executable: $ServerExe"
Write-Host "[CAI TEST] Working directory: $serverRootPath"
Write-Host "[CAI TEST] Arguments: $($args -join ' ')"

if ($NoStart) {
    Write-Host "[CAI TEST] -NoStart supplied. Command was not launched."
    return
}

Start-Process -FilePath $ServerExe -ArgumentList $args -WorkingDirectory $serverRootPath -WindowStyle Hidden
Write-Host "[CAI TEST] Local dedicated server start requested."
