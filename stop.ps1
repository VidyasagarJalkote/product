# PowerShell Script to Stop Application locally
# Usage: .\stop.ps1

Write-Host "Stopping any running uvicorn process on port 8000..." -ForegroundColor Yellow

$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connections) {
    foreach ($conn in $connections) {
        $procId = $conn.OwningProcess
        if ($procId -gt 0) {
            Write-Host "Killing process PID: $procId" -ForegroundColor Yellow
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "Server on port 8000 stopped." -ForegroundColor Green
} else {
    Write-Host "No process found running on port 8000." -ForegroundColor Green
}
