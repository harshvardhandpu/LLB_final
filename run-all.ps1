Write-Host "Starting Legal Document Analyzer..."

# Start MongoDB
Start-Process powershell -ArgumentList "-NoExit", "-Command", "mongod --dbpath .run/mongo-data"

# Start AI Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ai-service-python; python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt; python app/main.py"

# Start Auth Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd auth-service-python; pip install -r requirements.txt; python app.py"

# Start Spring Boot Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend-springboot; mvn spring-boot:run"

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install; npm run dev"

Write-Host ""
Write-Host "Application Started"
Write-Host "Frontend: http://localhost:3000"
