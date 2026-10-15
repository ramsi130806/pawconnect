@echo off
title PawConnect - Offline Server
echo =======================================================
echo   PawConnect - Heyvanlarin Sahiblendirilmese Sistemi
echo   Atlantia STEM Olympiad (SW01: Software Projects)
echo =======================================================
echo.
echo Server basladilir...
start http://localhost:8000
.\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
