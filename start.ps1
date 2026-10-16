# PowerShell Script to Start Application locally
# Usage: .\start.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting DevOps CRUD App (Local)        " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Ensure WSL PostgreSQL is running
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "[*] Checking PostgreSQL service..." -ForegroundColor Yellow
    wsl sudo service postgresql start | Out-Null
    Write-Host "[*] PostgreSQL service is active." -ForegroundColor Green
}

# 2. Check Python packages
Write-Host "[*] Verifying Python requirements..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

# 3. Launch App
Write-Host "`n[*] Starting FastAPI Application at http://localhost:8000" -ForegroundColor Green
Write-Host "[*] Swagger Documentation  at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[*] Press CTRL+C to stop the server.`n" -ForegroundColor Yellow

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
