$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    Write-Host "Creating isolated Python environment..."
    py -m venv (Join-Path $root ".venv")
    & $python -m pip install --upgrade pip
}

& $python -c "import PySide6, mido"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing missing isolated application dependencies..."
    & $python -m pip install -r (Join-Path $root "requirements.txt")
}

& $python (Join-Path $root "main.py")
