# prototype/scripts/start_meev_local.ps1
# Starts MEEV Backend (FastAPI) and Frontend (React) locally from inside the prototype directory

$PROTOTYPE_ROOT = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location -Path $PROTOTYPE_ROOT

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  MEEV — MPLADS Education Ecosystem Validator (SIH26102)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# 0. Hydrate initial database with schools and projects
Write-Host "[0/3] Hydrating UDISE+ and e-SAKSHI data..." -ForegroundColor Yellow
$env:PYTHONPATH = "."
py -3.11 -c "from backend.scripts.load_udise_data import load_schools; load_schools()"
py -3.11 -c "from backend.scripts.generate_synthetic_esakshi import generate_projects; generate_projects()"

# 1. Start Backend in background process
Write-Host "[1/3] Starting MEEV Core API on http://localhost:8000..." -ForegroundColor Yellow
Start-Process -FilePath "py" -ArgumentList "-3.11 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Minimized

Start-Sleep -Seconds 2

# 2. Start Frontend
Write-Host "[2/3] Launching MEEV React Dashboard on http://localhost:3000..." -ForegroundColor Yellow
Set-Location -Path "$PROTOTYPE_ROOT\frontend"
npm start
