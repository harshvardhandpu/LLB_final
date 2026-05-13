# ⚡ Quick Start Guide

Get the Legal Document Analyzer running in 15 minutes!

## Prerequisites Check

```bash
# Check Java version (should be 17+)
java -version

# Check Python version (should be 3.10+)
python --version

# Check Maven (should be 3.8.0+)
mvn --version
```

## 🏃 Quick Setup (Windows)

### Terminal 1: Python AI Service

```bash
cd c:\Users\Admin\OneDrive\Desktop\LLB\legal-document-analyzer\ai-service-python

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies (take ~10 min on first run)
pip install -r requirements.txt

# Run AI service
cd app
python main.py
```

✅ Wait for: `Running on http://0.0.0.0:5000`

### Terminal 2: Spring Boot Backend

```bash
cd c:\Users\Admin\OneDrive\Desktop\LLB\legal-document-analyzer\backend-springboot

# Build project (5-10 min first time)
mvn clean install

# Run backend
mvn spring-boot:run
```

✅ Wait for: `Started LegalDocumentAnalyzerApplication`

### Terminal 3: Frontend Server

```bash
cd c:\Users\Admin\OneDrive\Desktop\LLB\legal-document-analyzer\frontend

# Option A: Python server
python -m http.server 3000

# Option B: Node HTTP Server (if installed)
npx http-server -p 3000
```

✅ Open browser to: `http://localhost:3000`

## ✅ Verification Checklist

- [ ] Terminal 1 shows AI service healthy
- [ ] Terminal 2 shows Spring Boot started
- [ ] Terminal 3 shows frontend server running
- [ ] Browser loads frontend at localhost:3000
- [ ] Test button visible on webpage

## 🧪 Test Upload

1. Go to `http://localhost:3000`
2. Download sample: `sample-documents/rental-agreement.txt`
3. Convert to PDF (or upload .txt directly)
4. Upload file
5. Wait 30-60 seconds
6. Check results

## 📌 Important Notes

### First Run
- AI models (~4GB) download automatically
- Takes 5-10 minutes on first run
- Subsequent runs are much faster
- Needs stable internet connection

### Memory Requirements
- Python: 4-6GB
- Java: 2-4GB
- Total: 8GB+ recommended

### Port Requirements
- Python: 5000 (AI Service)
- Java: 8080 (Backend)
- Frontend: 3000 (or any available port)

## 🆘 If Something Goes Wrong

### AI Service Won't Start
```bash
# Check Python installation
python --version

# Try reinstalling packages
pip install --upgrade pip
pip install -r requirements.txt

# Try different port in main.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Backend Won't Start
```bash
# Check Java installation
java -version

# Clean build
mvn clean

# Try with verbose output
mvn spring-boot:run -X
```

### Frontend Won't Load
```bash
# Check if server is running
netstat -ano | findstr :3000

# Kill and restart
python -m http.server 3000
```

### Browser Shows CORS Error
- All CORS enabled by default
- Check that backend is on 8080 (not 8081, etc.)
- Refresh browser (Ctrl+Shift+Del to clear cache)

## 🎯 Next Steps

1. ✅ Complete setup above
2. ✅ Verify all 3 services running
3. ✅ Test with sample documents
4. ✅ Read full README.md for API details
5. ✅ Customize for your use case

## 📊 Example API Call

Once everything is running:

```bash
# Upload a document (on Windows PowerShell)
$filePath = "c:\Users\Admin\OneDrive\Desktop\LLB\legal-document-analyzer\sample-documents\rental-agreement.txt"
$fileContent = Get-Content $filePath -Raw

$jsonPayload = @{
    text = $fileContent
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8080/api/documents/analyze" `
  -Method Post `
  -ContentType "application/json" `
  -Body $jsonPayload
```

## ⏱️ Timeline

| Step | Time | Action |
|------|------|--------|
| 0:00 | - | Start terminals |
| 0:30 | Python | pip install in progress |
| 5:00 | All | mvn install in progress |
| 10:00 | Check | All services should be running |
| 15:00 | Test | Upload file and verify results |

---

🎉 **You're all set!** Start analyzing legal documents!

For detailed information, see README.md
