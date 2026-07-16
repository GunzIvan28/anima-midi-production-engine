$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent $root
$version = (Get-Content -LiteralPath (Join-Path $repo "VERSION") -Raw).Trim()
$distributionName = "ANIMA-MIDI-Production-Engine-$version"
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Run .\run.ps1 once to create the isolated environment."
}

Push-Location $root
try {
    # A previously launched packaged copy keeps Qt plugin DLLs (for example
    # qwebp.dll) open and prevents PyInstaller from replacing the dist tree.
    $running = Get-Process -Name "ANIMA-MIDI-Production-Engine*" -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host "Closing the running packaged ANIMA application before rebuilding..."
        $running | Stop-Process -Force
        $running | Wait-Process -Timeout 10 -ErrorAction SilentlyContinue
    }

    # Remove stale one-folder output. Resolve and verify both targets before a
    # recursive removal so this operation can never escape the app directory.
    $rootFull = [System.IO.Path]::GetFullPath($root).TrimEnd('\') + '\'
    foreach ($relative in @("build\anima_native", "dist\$distributionName")) {
        $target = [System.IO.Path]::GetFullPath((Join-Path $root $relative))
        if (-not $target.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to clean an unsafe build path: $target"
        }
        if (Test-Path -LiteralPath $target) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
    }

    & $python -m PyInstaller --clean --noconfirm "anima_native.spec"
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE. No completed application was produced."
    }
} finally {
    Pop-Location
}

Write-Host "Native application built at: $root\dist\$distributionName"
