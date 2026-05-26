function Assert-CampaignAIPythonPackage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ModRoot
    )

    $pythonRoot = Join-Path $ModRoot "python_code"
    if (!(Test-Path -LiteralPath $pythonRoot)) {
        throw "Missing Campaign AI Python folder: $pythonRoot"
    }

    $pythiaMarker = Join-Path $pythonRoot '$PYTHIA$'
    $requiredFiles = @(
        $pythiaMarker,
        (Join-Path $pythonRoot "__init__.py"),
        (Join-Path $pythonRoot "api.py")
    )

    foreach ($file in $requiredFiles) {
        if (!(Test-Path -LiteralPath $file)) {
            throw "Missing Campaign AI Python package file: $file"
        }

        if ((Get-Item -LiteralPath $file).Length -le 0) {
            throw "Campaign AI Python package file is empty: $file"
        }
    }

    $packageName = (Get-Content -LiteralPath $pythiaMarker -Raw).Trim()
    if ($packageName -ne "CAIPython") {
        throw "Unexpected Pythia package name '$packageName' in $pythiaMarker. Expected 'CAIPython'."
    }

    $apiPath = Join-Path $pythonRoot "api.py"
    $apiText = Get-Content -LiteralPath $apiPath -Raw
    if ($apiText -notmatch "def\s+ping\s*\(") {
        throw "Campaign AI Python API is missing ping() in $apiPath."
    }

    Write-Host "[CAI BUILD] Python package validated: $packageName at $pythonRoot"
}

