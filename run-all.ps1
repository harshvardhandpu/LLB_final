$ErrorActionPreference = "Stop"

$PROJECT_ROOT = $PSScriptRoot
$AI_VENV = Join-Path $PROJECT_ROOT ".ai-venv"
$AI_APP = Join-Path $PROJECT_ROOT "ai-service-python\app\main.py"
$BACKEND_JAR = Join-Path $PROJECT_ROOT "backend-springboot\target\legal-document-analyzer-1.0.0.jar"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "frontend"
$AUTH_DIR = Join-Path $PROJECT_ROOT "auth-service-python"

$PID_DIR = Join-Path $PROJECT_ROOT ".run"
$LOG_DIR = Join-Path $PID_DIR "logs"

$AI_PID_FILE = Join-Path $PID_DIR "ai.pid"
$BACKEND_PID_FILE = Join-Path $PID_DIR "backend.pid"
$FRONTEND_PID_FILE = Join-Path $PID_DIR "frontend.pid"
$AUTH_PID_FILE = Join-Path $PID_DIR "auth.pid"
$MONGO_PID_FILE = Join-Path $PID_DIR "mongodb.pid"

$AI_LOG = Join-Path $LOG_DIR "ai.log"
$AI_ERR = Join-Path $LOG_DIR "ai.err"
$BACKEND_LOG = Join-Path $LOG_DIR "backend.log"
$BACKEND_ERR = Join-Path $LOG_DIR "backend.err"
$FRONTEND_LOG = Join-Path $LOG_DIR "frontend.log"
$FRONTEND_ERR = Join-Path $LOG_DIR "frontend.err"
$AUTH_LOG = Join-Path $LOG_DIR "auth.log"
$AUTH_ERR = Join-Path $LOG_DIR "auth.err"
$MONGO_LOG = Join-Path $LOG_DIR "mongodb.log"
$MONGO_ERR = Join-Path $LOG_DIR "mongodb.err"

function Require-Command {
    param([string]$cmd)
    if (!(Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "Missing required command: $cmd"
        exit 1
    }
}

function Is-Running {
    param([string]$pid_file)
    if (Test-Path $pid_file) {
        $pid_val = Get-Content $pid_file
        if (![string]::IsNullOrWhiteSpace($pid_val)) {
            $process = Get-Process -Id $pid_val -ErrorAction SilentlyContinue
            if ($process) {
                return $true
            }
        }
        Remove-Item -Path $pid_file -Force
    }
    return $false
}

function Wait-For-Url {
    param(
        [string]$url,
        [string]$name,
        [int]$attempts = 60,
        [int]$delay = 2
    )

    for ($i = 1; $i -le $attempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            Write-Host "$name is ready: $url"
            return $true
        } catch {
            Start-Sleep -Seconds $delay
        }
    }

    Write-Error "$name did not become ready in time. Check logs in $LOG_DIR"
    return $false
}

if (!(Test-Path $PID_DIR)) { New-Item -ItemType Directory -Path $PID_DIR | Out-Null }
if (!(Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR | Out-Null }

Require-Command "python"
Require-Command "java"

$pythonCmd = Join-Path $AI_VENV "Scripts\python.exe"

if (!(Test-Path $pythonCmd)) {
    Write-Error "AI virtual environment not found at $AI_VENV"
    Write-Host "Create it first with:"
    Write-Host "  python -m venv .ai-venv"
    Write-Host "  .\.ai-venv\Scripts\activate"
    Write-Host "  pip install --upgrade pip"
    Write-Host "  pip install `"Flask>=3.0.0,<4.0.0`" `"Flask-CORS>=4.0.0`" `"transformers>=4.30.0,<5.0.0`" `"sentencepiece>=0.1.99`" `"protobuf>=4.20.0,<5.0.0`" `"requests>=2.31.0,<3.0.0`""
    Write-Host "  pip install `"torch==2.3.1`" --index-url https://download.pytorch.org/whl/cpu"
    exit 1
}

if (!(Test-Path $BACKEND_JAR)) {
    Write-Error "Backend jar not found at $BACKEND_JAR"
    Write-Host "Build it first, for example with Maven (mvn clean package in backend-springboot)."
    exit 1
}

$MONGO_BIN = "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"
$MONGO_DBPATH = Join-Path $PROJECT_ROOT ".mongodb-data"

if (!(Test-Path $MONGO_BIN)) {
    Write-Error "MongoDB binary not found at $MONGO_BIN"
    exit 1
}

if (!(Test-Path $MONGO_DBPATH)) { 
    Write-Host "Creating MongoDB data directory..."
    New-Item -ItemType Directory -Path $MONGO_DBPATH | Out-Null 
}

if (!(Is-Running $MONGO_PID_FILE)) {
    Write-Host "Starting MongoDB..."
    $proc = Start-Process -FilePath $MONGO_BIN -ArgumentList "--dbpath", "`"$MONGO_DBPATH`"" -WindowStyle Hidden -RedirectStandardOutput $MONGO_LOG -RedirectStandardError $MONGO_ERR -PassThru
    $proc.Id | Out-File $MONGO_PID_FILE -Encoding ASCII
} else {
    Write-Host "MongoDB already running"
}

if (!(Is-Running $AI_PID_FILE)) {
    Write-Host "Starting AI service..."
    $env:HF_HOME = Join-Path $PROJECT_ROOT ".huggingface-cache"
    $proc = Start-Process -FilePath $pythonCmd -ArgumentList "`"$AI_APP`"" -WindowStyle Hidden -RedirectStandardOutput $AI_LOG -RedirectStandardError $AI_ERR -PassThru
    $proc.Id | Out-File $AI_PID_FILE -Encoding ASCII
} else {
    Write-Host "AI service already running"
}

if (!(Is-Running $BACKEND_PID_FILE)) {
    Write-Host "Starting Spring backend..."
    $proc = Start-Process -FilePath "java" -ArgumentList "-jar", "`"$BACKEND_JAR`"" -WindowStyle Hidden -RedirectStandardOutput $BACKEND_LOG -RedirectStandardError $BACKEND_ERR -PassThru
    $proc.Id | Out-File $BACKEND_PID_FILE -Encoding ASCII
} else {
    Write-Host "Spring backend already running"
}

# --- Auth Service ---
$AUTH_VENV = Join-Path $AUTH_DIR ".venv"
$AUTH_APP = Join-Path $AUTH_DIR "app.py"

if (!(Test-Path (Join-Path $AUTH_VENV "Scripts\python.exe"))) {
    Write-Host "Creating auth service virtual environment..."
    $pythonBaseCmd = "python"
    Start-Process -FilePath $pythonBaseCmd -ArgumentList "-m", "venv", "`"$AUTH_VENV`"" -Wait -NoNewWindow
    
    $authPipCmd = Join-Path $AUTH_VENV "Scripts\pip.exe"
    $authReqs = Join-Path $AUTH_DIR "requirements.txt"
    Write-Host "Installing auth service dependencies..."
    Start-Process -FilePath $authPipCmd -ArgumentList "install", "-r", "`"$authReqs`"" -Wait -NoNewWindow
}

$authPythonCmd = Join-Path $AUTH_VENV "Scripts\python.exe"

if (!(Is-Running $AUTH_PID_FILE)) {
    Write-Host "Starting Auth service..."
    $proc = Start-Process -FilePath $authPythonCmd -ArgumentList "`"$AUTH_APP`"" -WindowStyle Hidden -RedirectStandardOutput $AUTH_LOG -RedirectStandardError $AUTH_ERR -PassThru
    $proc.Id | Out-File $AUTH_PID_FILE -Encoding ASCII
} else {
    Write-Host "Auth service already running"
}

if (!(Is-Running $FRONTEND_PID_FILE)) {
    Write-Host "Starting React frontend..."
    # Execute npm run dev and capture PID
    $npmCmd = "npm.cmd"
    $proc = Start-Process -FilePath $npmCmd -ArgumentList "run", "dev" -WorkingDirectory $FRONTEND_DIR -WindowStyle Hidden -RedirectStandardOutput $FRONTEND_LOG -RedirectStandardError $FRONTEND_ERR -PassThru
    $proc.Id | Out-File $FRONTEND_PID_FILE -Encoding ASCII
} else {
    Write-Host "Frontend already running"
}

Wait-For-Url "http://127.0.0.1:5000/health" "AI service" 180 2
Wait-For-Url "http://127.0.0.1:5001/api/auth/me" "Auth service" 60 2
Wait-For-Url "http://127.0.0.1:8080/api/documents/health" "Spring backend" 60 2
Wait-For-Url "http://127.0.0.1:3000" "Frontend" 60 2

Write-Host "`nApplication started successfully.`n"
Write-Host "Open in browser:"
Write-Host "  http://localhost:3000`n"
Write-Host "Logs:"
Write-Host "  $AI_LOG"
Write-Host "  $BACKEND_LOG"
Write-Host "  $FRONTEND_LOG`n"
Write-Host "To stop everything:"
Write-Host "  .\stop-all.ps1 or run stop-all.bat"
