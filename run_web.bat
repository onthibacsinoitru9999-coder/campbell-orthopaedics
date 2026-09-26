@echo off
title Campbell Operative Orthopaedics Web Navigator
cd /d "%~dp0"
echo ========================================================
echo   CAMPBELL OPERATIVE ORTHOPAEDICS (13TH ED)
echo   He thong Tra cuu Phau thuat & Giai phau
echo ========================================================
echo Dang khoi dong Web Server tai http://localhost:8000 ...
python -m uvicorn server:app --host 0.0.0.0 --port 8000
pause
