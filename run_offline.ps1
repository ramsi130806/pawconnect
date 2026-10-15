# PawConnect Offline Launcher for Atlântia Olympiad (Rule SW01.5.9)
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  PawConnect - Heyvanların Sahibləndirilməsi Sistemi" -ForegroundColor Yellow
Write-Host "  Atlântia International STEM Olympiad (SW01)" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server başladılır və brauzer açılır..." -ForegroundColor White

Start-Process "http://localhost:8000"
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
