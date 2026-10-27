$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 or newer is required.' }
    & $pythonPath -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Could not install application dependencies.' }
}
& $pythonPath -c "import importlib.util, sys; sys.exit(0 if all(importlib.util.find_spec(name) for name in ('flask','flask_wtf','oracledb')) else 1)"
if ($LASTEXITCODE -ne 0) {
    & $pythonPath -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Could not install Oracle application dependencies.' }
}
& $pythonPath -m flask --app run oracle-check
if ($LASTEXITCODE -ne 0) { throw 'Oracle is not ready. Run .venv\Scripts\python.exe scripts\setup_oracle.py first. See README.md.' }
Write-Host 'Atelier is opening at http://127.0.0.1:5000'
Start-Process 'http://127.0.0.1:5000'
& $pythonPath run.py
