# PowerShell Script to Export PostgreSQL Database Dump
# Usage: .\scripts\export_dump.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$OutputFile = Join-Path $ProjectRoot "devops_db_dump.sql"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Database Export (pg_dump)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if pg_dump is available directly in Windows
if (Get-Command pg_dump -ErrorAction SilentlyContinue) {
    Write-Host "[*] Found pg_dump in Windows environment. Exporting..." -ForegroundColor Yellow
    $env:PGPASSWORD = "postgres"
    pg_dump -U postgres -h localhost -p 5432 -d devops_db --clean --if-exists -F p -f "$OutputFile"
}
# Otherwise check if WSL is available with pg_dump
elseif (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "[*] Using WSL Ubuntu pg_dump utility..." -ForegroundColor Yellow
    $forwardSlashPath = $OutputFile -replace '\\', '/'
    $wslOutputPath = (wsl wslpath -a -u "$forwardSlashPath").Trim()
    wsl bash -c "PGPASSWORD=postgres pg_dump -U postgres -h localhost -p 5432 -d devops_db --clean --if-exists -F p -f '$wslOutputPath'"
}
# Fallback to Python export
else {
    Write-Host "[*] Using Python fallback exporter..." -ForegroundColor Yellow
    python -c "import sys; sys.path.append(r'$ProjectRoot'); from app.crud import export_sql_dump; open(r'$OutputFile', 'w', encoding='utf-8').write(export_sql_dump())"
}

if (Test-Path $OutputFile) {
    $fileSize = (Get-Item $OutputFile).Length
    Write-Host "`n[SUCCESS] Database dump created successfully!" -ForegroundColor Green
    Write-Host "File Location : $OutputFile" -ForegroundColor White
    Write-Host "File Size     : $fileSize bytes" -ForegroundColor White
    Write-Host "Next Step     : Transfer this file to your production server using SCP." -ForegroundColor Cyan
} else {
    Write-Host "`n[ERROR] Failed to create database dump file." -ForegroundColor Red
}
