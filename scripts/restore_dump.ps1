# PowerShell Script to Restore Database Dump onto Target/Production Database
# Usage: .\scripts\restore_dump.ps1 [-TargetHost "localhost"] [-TargetPort 5432] [-TargetDb "devops_db"] [-TargetUser "postgres"] [-DumpFile "devops_db_dump.sql"]

param(
    [string]$TargetHost = "localhost",
    [int]$TargetPort = 5432,
    [string]$TargetDb = "devops_db",
    [string]$TargetUser = "postgres",
    [string]$DumpFile = "devops_db_dump.sql"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

if (-not [System.IO.Path]::IsPathRooted($DumpFile)) {
    $DumpFile = Join-Path $ProjectRoot $DumpFile
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Database Restore (psql)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if (-not (Test-Path $DumpFile)) {
    Write-Host "[ERROR] Dump file not found: $DumpFile" -ForegroundColor Red
    Write-Host "Please run .\scripts\export_dump.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "[*] Target Host     : $TargetHost`:$TargetPort" -ForegroundColor White
Write-Host "[*] Target Database : $TargetDb" -ForegroundColor White
Write-Host "[*] Target User     : $TargetUser" -ForegroundColor White
Write-Host "[*] Source Dump File: $DumpFile" -ForegroundColor White

if (Get-Command psql -ErrorAction SilentlyContinue) {
    Write-Host "[*] Restoring using Windows psql..." -ForegroundColor Yellow
    psql -h $TargetHost -p $TargetPort -U $TargetUser -d $TargetDb -f "$DumpFile"
}
elseif (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "[*] Restoring using WSL Ubuntu psql..." -ForegroundColor Yellow
    $forwardSlashPath = $DumpFile -replace '\\', '/'
    $wslDumpPath = (wsl wslpath -a -u "$forwardSlashPath").Trim()
    wsl bash -c "PGPASSWORD=postgres psql -h '$TargetHost' -p $TargetPort -U '$TargetUser' -d '$TargetDb' -f '$wslDumpPath'"
}
else {
    Write-Host "[ERROR] Neither psql nor WSL was found. Please install postgresql-client." -ForegroundColor Red
    exit 1
}

Write-Host "`n[SUCCESS] Database restore completed successfully!" -ForegroundColor Green
