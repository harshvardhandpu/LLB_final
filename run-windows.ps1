Write-Host ""
Write-Host "========================================="
Write-Host " LEGAL DOCUMENT ANALYZER - WINDOWS START "
Write-Host "========================================="
Write-Host ""

# Create runtime folders
if (!(Test-Path ".run")) {
    New-Item -ItemType Directory -Path ".run"
}

if (!(Test-Path ".run\mongo-data")) {
    New-Item -ItemType Directory -Path ".run\mongo-data"
}

# Create Python virtual environment
if (!(Test-Path ".ai-venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv .ai-venv
}

# Activate virtual environment
& ".\.ai-venv\Scripts\Activate.ps1"

# Install AI service dependencies
Write-Host ""
Write-Host "Installing AI service dependencies..."
pip install -r ai-service-python\requirements.txt

# Install Auth service dependencies
Write-Host ""
Write-Host "Installing Auth service dependencies..."
pip install -r auth-service-python\requirements.txt

# Install frontend dependencies
Write-Host ""
Write-Host "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Build Spring Boot backend
Write-Host ""
Write-Host "Building Spring Boot backend..."
cd backend-springboot
mvn clean install -DskipTests
cd ..

# Start MongoDB
Write-Host ""
Write-Host "Starting MongoDB..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "mongod --dbpath .run/mongo-data"

# Start AI service
Write-Host "Starting AI Service..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.ai-venv\Scripts\Activate.ps1; python ai-service-python\app\main.py"

# Start Auth service
Write-Host "Starting Auth Service..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.ai-venv\Scripts\Activate.ps1; python auth-service-python\app.py"

# Start Spring backend
Write-Host "Starting Spring Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend-springboot'; mvn spring-boot:run"

# Start Frontend
Write-Host "Starting Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Write-Host ""
Write-Host "========================================="
Write-Host " APPLICATION STARTED SUCCESSFULLY "
Write-Host "========================================="
Write-Host ""
Write-Host "Frontend URL:"
Write-Host "http://localhost:3000"
Write-Host ""
