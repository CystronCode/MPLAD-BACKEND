@echo off
title MEEV - SIH26102 Prototype Launcher
echo ==========================================================
echo   MEEV - MPLADS Education Ecosystem Validator (SIH26102)
echo ==========================================================

cd /d "%~dp0"
set PYTHONPATH=.

echo [1/3] Ingesting authentic UDISE+ and real-time e-SAKSHI data...
python backend/scripts/load_realtime_data.py

echo [2/3] Starting FastAPI Backend on http://localhost:8000...
start "MEEV Backend" python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

timeout /t 2 /nobreak >nul

echo [3/3] Launching React Frontend on http://localhost:3000...
cd frontend
call npm start

