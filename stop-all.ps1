$ErrorActionPreference = "Stop"

$PROJECT_ROOT = $PSScriptRoot
$PID_DIR = Join-Path $PROJECT_ROOT ".run"

function Stop-From-Pid-File {
    param(
        [string]$pid_file,
        [string]$name
    )

    if (!(Test-Path $pid_file)) {
        Write-Host "$name is not running"
        return
    }

    $pid_val = Get-Content $pid_file
    if (![string]::IsNullOrWhiteSpace($pid_val)) {
        $process = Get-Process -Id $pid_val -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Stopping $name (pid $pid_val)"
            $process | Stop-Process -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "$name is not running"
        }
    } else {
        Write-Host "$name is not running"
    }

    Remove-Item -Path $pid_file -Force -ErrorAction SilentlyContinue
}

Stop-From-Pid-File (Join-Path $PID_DIR "ai.pid") "AI service"
Stop-From-Pid-File (Join-Path $PID_DIR "backend.pid") "Spring backend"
Stop-From-Pid-File (Join-Path $PID_DIR "auth.pid") "Auth service"
Stop-From-Pid-File (Join-Path $PID_DIR "frontend.pid") "Frontend"
Stop-From-Pid-File (Join-Path $PID_DIR "mongodb.pid") "MongoDB"

Write-Host "All services processed."
