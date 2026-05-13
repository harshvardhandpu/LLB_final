# 🔧 Configuration & Setup Guide

Complete configuration guide for Legal Document Analyzer

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Backend Configuration](#backend-configuration)
4. [AI Service Configuration](#ai-service-configuration)
5. [Frontend Configuration](#frontend-configuration)
6. [Database Setup (Optional)](#database-setup-optional)
7. [Docker Setup (Optional)](#docker-setup-optional)
8. [Production Deployment](#production-deployment)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**: 8GB
- **CPU**: Quad-core 2.0GHz+
- **Disk**: 20GB free space
- **Internet**: For model downloads (500MB minimum)

### Recommended Requirements
- **RAM**: 16GB+
- **GPU**: NVIDIA (CUDA 11.8+) or M1/M2 for faster processing
- **CPU**: 8+ cores
- **Disk**: 50GB SSD
- **Internet**: Fiber or broadband

### Software
- **Java**: JDK 17+ (LTS recommended)
- **Python**: 3.10 or 3.11
- **Maven**: 3.8.0+
- **Git**: Latest version

---

## Environment Setup

### Windows Setup

#### 1. Install Java JDK 17

```cmd
# Download from https://adoptium.net/
# Or use Chocolatey (if installed)
choco install adoptopenjdk17

# Verify installation
java -version
javac -version
```

#### 2. Set JAVA_HOME Environment Variable

1. Open Start → Search "Environment Variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "System variables", click "New"
5. Variable name: `JAVA_HOME`
6. Variable value: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x` (adjust path as needed)
7. Click OK and restart terminal

Verify:
```cmd
echo %JAVA_HOME%
```

#### 3. Install Maven

```cmd
# Download from https://maven.apache.org/download.cgi
# Extract to a folder, e.g., C:\maven

# Add to PATH environment variable
# Variable name: PATH
# Add: C:\maven\bin

mvn --version
```

#### 4. Install Python

```cmd
# Download from https://www.python.org/downloads/
# Or use Chocolatey
choco install python310

python --version
```

### macOS Setup

```bash
# Using Homebrew
brew install openjdk@17
brew install maven
brew install python@3.10

# Set JAVA_HOME in ~/.zshrc or ~/.bash_profile
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH=$JAVA_HOME/bin:$PATH

# Verify
java -version
mvn --version
python --version
```

### Linux (Ubuntu) Setup

```bash
# Update packages
sudo apt update
sudo apt upgrade

# Install Java
sudo apt install openjdk-17-jdk

# Install Maven
sudo apt install maven

# Install Python
sudo apt install python3.10 python3-pip

# Verify
java -version
mvn --version
python3 --version
```

---

## Backend Configuration

### Spring Boot Configuration

#### File: `backend-springboot/src/main/resources/application.properties`

```properties
# Server Configuration
server.port=8080
server.servlet.context-path=/api
server.error.include-message=always
server.error.include-binding-errors=always

# File Upload Configuration
spring.servlet.multipart.max-file-size=50MB
spring.servlet.multipart.max-request-size=50MB
upload.dir=./uploads

# AI Service Configuration
ai.service.url=http://localhost:5000
ai.service.timeout=120000
ai.service.analyze-endpoint=/analyze
ai.service.extract-entities-endpoint=/extract-entities
ai.service.classify-clauses-endpoint=/classify-clauses
ai.service.summarize-endpoint=/summarize
ai.service.simplify-endpoint=/simplify
ai.service.risk-analysis-endpoint=/risk-analysis

# Logging Configuration
logging.level.root=INFO
logging.level.com.legalanalyzer=DEBUG
logging.level.org.springframework.web=INFO
logging.pattern.console=%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n

# Actuator Configuration
management.endpoints.web.exposure.include=health,info,metrics

# Connection Pool Configuration
server.tomcat.threads.max=200
server.tomcat.threads.min-spare=10
```

### Building Backend

```bash
cd backend-springboot

# Full clean install
mvn clean install

# Skip tests (faster)
mvn clean install -DskipTests

# With specific Java version
mvn -Dorg.slf4j.simpleLogger.defaultLogLevel=debug clean install
```

### Running Backend with Custom Configuration

```bash
# Run with custom port
mvn spring-boot:run -Dspring-boot.run.arguments="--server.port=9090"

# Run with increased memory
set MAVEN_OPTS=-Xmx4g
mvn spring-boot:run

# Run JAR directly
mvn clean package
java -Xmx4g -jar target/legal-document-analyzer-1.0.0.jar
```

---

## AI Service Configuration

### Python Configuration

#### File: `ai-service-python/app/main.py`

```python
# Model Selection
# Options: "facebook/bart-large-cnn", "t5-base", "google/pegasus-xsum"
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"

# Classification Model
# Options: "facebook/bart-large-mnli", "roberta-large-mnli"
CLASSIFICATION_MODEL = "facebook/bart-large-mnli"

# Text Generation Model
# Options: "gpt2", "distilgpt2"
GENERATION_MODEL = "gpt2"

# Risk Analysis Thresholds
HIGH_PENALTY_THRESHOLD = 100000  # Rs.
RISK_CONFIDENCE_THRESHOLD = 0.7

# Processing Configuration
MAX_CHUNK_LENGTH = 1024
DOCUMENT_LENGTH_LIMIT = 65000
```

### Python Environment Configuration

#### File: `.env` in `ai-service-python/`

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Hugging Face
HF_HOME=./models
TRANSFORMERS_CACHE=./models

# Logging
LOG_LEVEL=INFO

# GPU Configuration (if available)
CUDA_VISIBLE_DEVICES=0
```

### Installing with GPU Support

```bash
cd ai-service-python

# Activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install with CUDA support (example for CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other requirements
pip install -r requirements.txt

# Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

### Running AI Service with Custom Configuration

```bash
cd ai-service-python/app

# Run on custom port
python main.py
# Then edit in main.py: app.run(port=5001)

# Run with custom models
export HF_HOME=/custom/model/path
python main.py

# Run with production server (Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

---

## Frontend Configuration

### File: `frontend/js/app.js`

```javascript
// API Configuration
const API_URL = 'http://localhost:8080/api';
const AI_SERVICE_URL = 'http://localhost:5000';

// File Upload Configuration
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt'];

// UI Configuration
const ANALYSIS_TIMEOUT = 120000; // 2 minutes
const RESULTS_SCROLL_DELAY = 500; // milliseconds
```

### Running Frontend Locally

#### Option 1: Python HTTP Server
```bash
cd frontend
python -m http.server 3000
# Open: http://localhost:3000
```

#### Option 2: Node.js HTTP Server
```bash
cd frontend
npx http-server -p 3000
```

#### Option 3: Using Live Server in VS Code

1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

#### Option 4: Node.js Express Server
```bash
cd frontend
npm init -y
npm install express cors
```

Create `server.js`:
```javascript
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname)));
app.listen(3000, () => console.log('Frontend running on 3000'));
```

Then run:
```bash
node server.js
```

---

## Database Setup (Optional)

For production deployment with history storage:

### PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE legal_analyzer;

-- Create tables
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_size INT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_status VARCHAR(50),
    file_path VARCHAR(500)
);

CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id),
    summary TEXT,
    risks JSONB,
    clauses JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_date ON documents(upload_date);
CREATE INDEX idx_document_status ON documents(analysis_status);
```

### Add to Spring Boot

#### File: `backend-springboot/pom.xml`

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.0</version>
</dependency>
```

#### File: `application.properties`

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/legal_analyzer
spring.datasource.username=postgres
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false
spring.jpa.database-platform=org.hibernate.dialect.PostgreSQLDialect
```

---

## Docker Setup (Optional)

### Dockerfile for Backend

Create `backend-springboot/Dockerfile`:

```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/legal-document-analyzer-1.0.0.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Dockerfile for AI Service

Create `ai-service-python/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app/main.py"]
```

### Docker Compose

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  ai-service:
    build: ./ai-service-python
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - HF_HOME=/models
    volumes:
      - ./models:/models
    container_name: legal-analyzer-ai

  backend:
    build: ./backend-springboot
    ports:
      - "8080:8080"
    depends_on:
      - ai-service
    environment:
      - AI_SERVICE_URL=http://ai-service:5000
    container_name: legal-analyzer-backend

  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
    container_name: legal-analyzer-frontend
```

Run with:
```bash
docker-compose up
```

---

## Production Deployment

### Cloud Deployment Considerations

#### AWS Deployment

1. **EC2 Instance** (t3.xlarge recommended)
   - 8GB RAM minimum
   - 100GB storage

2. **Load Balancer** (ALB or NLB)
   - Spring Boot: Port 8080
   - AI Service: Port 5000

3. **Security Groups**
   - Allow ports: 80, 443 (frontend), 8080 (backend), 5000 (AI service)

4. **RDS** (optional database)
   - PostgreSQL 14+

#### Azure Deployment

1. **App Service** for Spring Boot
2. **Container Instances** for Python service
3. **Storage Account** for uploads
4. **Application Insights** for monitoring

### SSL/HTTPS Configuration

For production, use HTTPS:

#### Spring Boot with SSL

```properties
server.ssl.key-store=classpath:keystore.p12
server.ssl.key-store-password=your_password
server.ssl.key-store-type=PKCS12
server.http2.enabled=true
```

#### NGINX Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name legal-analyzer.example.com;

    ssl_certificate /etc/letsencrypt/live/legal-analyzer.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/legal-analyzer.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8080/api;
    }
}
```

### Authentication & Authorization

Add to Spring Boot for production:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>

<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt</artifactId>
    <version>0.12.3</version>
</dependency>
```

---

## Performance Tuning

### JVM Optimization

```bash
# Increase heap size
export MAVEN_OPTS="-Xmx4g -XX:+UseG1GC"

# Enable parallel processing
export MAVEN_OPTS="-Xmx4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"
```

### Python Optimization

```bash
# Use PyPy for faster execution
pip install pypy3

# Or use Cython compilation
pip install Cython
```

### Database Indexing

```sql
-- Create indexes for faster queries
CREATE INDEX idx_analysis_date ON analyses(created_at);
CREATE INDEX idx_document_filename ON documents(filename);
CREATE INDEX idx_risk_type ON analyses USING gin(risks);
```

---

For additional help, consult README.md and API_DOCUMENTATION.md
