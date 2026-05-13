# 🏛️ Legal Document Analyzer for Indian Contracts

An AI-powered system for analyzing legal documents with a focus on Indian legal context (Bharatiya Nyaya Sanhita, Indian Contract Act, etc.).

## 🎯 Features

- **Document Upload**: Support for PDF and DOCX files (up to 50MB)
- **Information Extraction**: Automatically extract parties, dates, amounts, locations
- **Clause Classification**: Identify liability, termination, penalties, indemnification, etc.
- **Document Summarization**: Generate concise TL;DR summaries
- **Legal Simplification**: Convert complex legal jargon to plain English
- **Risk Analysis**: Detect high penalties, one-sided clauses, missing termination clauses
- **Pros & Cons Analysis**: Highlight favorable and unfavorable terms
- **Indian Legal Context**: Optimized for Indian legal documents and terminology

## 🏗️ Architecture

```
Legal Document Analyzer
├── Frontend (HTML, CSS, JavaScript)
│   ├── File upload interface
│   ├── Results dashboard
│   └── Real-time API communication
├── Backend (Spring Boot - Java)
│   ├── REST APIs
│   ├── File handling (PDF/DOCX parsing)
│   └── AI Service orchestration
└── AI Service (Python - Flask)
    ├── NLP Pipeline
    ├── Entity extraction
    ├── Clause classification
    ├── Summarization
    ├── Text simplification
    └── Risk analysis
```

## 📋 Project Structure

```
legal-document-analyzer/
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── backend-springboot/
│   ├── pom.xml
│   ├── src/
│   │   └── main/
│   │       ├── java/
│   │       │   └── com/legalanalyzer/
│   │       │       ├── LegalDocumentAnalyzerApplication.java
│   │       │       ├── controller/
│   │       │       │   └── DocumentController.java
│   │       │       ├── service/
│   │       │       │   └── DocumentAnalysisService.java
│   │       │       ├── model/
│   │       │       │   ├── AnalysisResponse.java
│   │       │       │   ├── KeyClause.java
│   │       │       │   ├── Risk.java
│   │       │       │   └── DocumentUpload.java
│   │       │       └── util/
│   │       │           ├── DocumentParser.java
│   │       │           └── AIServiceClient.java
│   │       └── resources/
│   │           └── application.properties
├── ai-service-python/
│   ├── requirements.txt
│   ├── app/
│   │   └── main.py
├── sample-documents/
│   ├── rental-agreement.txt
│   └── employment-agreement.txt
└── README.md
```

## 🛠️ Prerequisites

- **Java**: JDK 17 or higher
- **Python**: Python 3.10 or higher (with pip)
- **Maven**: 3.8.0 or higher
- **RAM**: 8GB minimum (for deep learning models)
- **Disk Space**: 10GB minimum

## 📦 Installation & Setup

### Step 1: Clone or Download the Project

```bash
cd c:\Users\Admin\OneDrive\Desktop\LLB\legal-document-analyzer
```

### Step 2: Setup Python AI Service

#### 2.1 Create Python Virtual Environment

```bash
cd ai-service-python
python -m venv venv
venv\Scripts\activate  # On Windows
```

#### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes as it downloads transformer models (~4GB). First run will download models automatically.

#### 2.3 Run AI Service

```bash
cd app
python main.py
```

The AI service will start on `http://localhost:5000`

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 3: Setup Spring Boot Backend

#### 3.1 Build the Project

```bash
cd backend-springboot
mvn clean install
```

This will download all dependencies and compile the project (first run may take 5-10 minutes).

#### 3.2 Run Spring Boot Application

```bash
mvn spring-boot:run
```

The backend will start on `http://localhost:8080/api`

You should see:
```
Started LegalDocumentAnalyzerApplication in X seconds
```

### Step 4: Setup Frontend

#### 4.1 Serve Frontend Files

Option A - Using Python (if available):
```bash
cd frontend
python -m http.server 3000
```

Option B - Using Node.js (if installed):
```bash
cd frontend
npx http-server -p 3000
```

Option C - Using VS Code Live Server:
- Install "Live Server" extension
- Right-click index.html → Open With Live Server

Frontend will be available at `http://localhost:3000` (or as shown in your server)

## ✅ Verification

### 1. Test AI Service Health

Open browser to: `http://localhost:5000/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "Legal Document Analyzer AI Service",
  "version": "1.0.0"
}
```

### 2. Test AI Service with Sample

Open browser to: `http://localhost:5000/test`

This will process a sample document and show analysis results.

### 3. Test Backend Health

Open browser to: `http://localhost:8080/api/documents/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "Legal Document Analyzer API",
  "version": "1.0.0"
}
```

### 4. Test Frontend

Open browser to: `http://localhost:3000`

Upload a test document to verify all components work together.

## 🚀 Usage

### Via Web Interface

1. Open `http://localhost:3000` in your browser
2. Click "Choose File" or drag & drop a PDF/DOCX document
3. Wait for analysis (takes 30-60 seconds for first run as models load)
4. Review results including:
   - Summary (TL;DR)
   - Extracted information (parties, dates, amounts)
   - Key clauses (liability, termination, etc.)
   - Identified risks with severity levels
   - Pros and cons
   - Simplified plain English version
5. Download report as JSON

### Via API (cURL Examples)

#### Upload and Analyze Document

```bash
curl -X POST http://localhost:8080/api/documents/analyze \
  -F "file=@sample-documents/rental-agreement.txt" \
  -H "Accept: application/json"
```

Response includes:
```json
{
  "fileName": "rental-agreement.txt",
  "summary": "This is a residential lease agreement between Rajesh Kumar (Landlord) and Amit Patel (Tenant)...",
  "simplified_text": "The landlord agrees to rent out the apartment...",
  "key_clauses": [...],
  "risks": [...],  
  "pros": [...],
  "cons": [...],
  "extracted_entities": {
    "parties": ["Rajesh Kumar", "Amit Patel"],
    "dates": ["15th day of January, 2024"],
    "amounts": ["Rs. 45,000/-", "Rs. 1,35,000/-"],
    "sections_found": 10
  },
  "status": "completed"
}
```

#### Direct AI Service Endpoints

```bash
# Summarize
curl -X POST http://localhost:5000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your legal text here..."}'

# Extract Entities
curl -X POST http://localhost:5000/extract-entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Your legal text here..."}'

# Classify Clauses
curl -X POST http://localhost:5000/classify-clauses \
  -H "Content-Type: application/json" \
  -d '{"text": "Your legal text here..."}'

# Analyze Risks
curl -X POST http://localhost:5000/risk-analysis \
  -H "Content-Type: application/json" \
  -d '{"text": "Your legal text here..."}'
```

## 📊 Sample Documents

### Included Test Documents

1. **rental-agreement.txt** - Sample residential lease agreement
   - Demonstrates extraction of rental amount, security deposit, termination clauses
   - Shows detection of liability and indemnification clauses

2. **employment-agreement.txt** - Sample employment contract
   - Demonstrates salary, benefits, and confidentiality extraction
   - Shows detection of non-compete and termination clauses

### To Test With Sample Documents

1. Use the sample documents in `sample-documents/` folder
2. Convert them to PDF using any PDF converter if needed
3. Upload through the web interface

## 🔍 API Endpoints

### Backend (Spring Boot) - `http://localhost:8080/api`

| Endpoint | Method | Description | Input | Output |
|----------|--------|-------------|-------|--------|
| `/documents/analyze` | POST | Upload and analyze document | File (PDF/DOCX) | AnalysisResponse JSON |
| `/documents/health` | GET | Health check | - | Status JSON |
| `/documents/docs` | GET | API documentation | - | Docs JSON |

### AI Service (Python Flask) - `http://localhost:5000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/analyze` | POST | Complete document analysis |
| `/extract-entities` | POST | Extract parties, dates, amounts |
| `/classify-clauses` | POST | Classify clause types |
| `/summarize` | POST | Generate summary |
| `/simplify` | POST | Simplify legal text |
| `/risk-analysis` | POST | Analyze risks and issues |
| `/test` | GET | Test with sample document |

## ⚙️ Configuration

### Backend Configuration (application.properties)

```properties
# Server
server.port=8080
server.servlet.context-path=/api

# File Upload
spring.servlet.multipart.max-file-size=50MB
spring.servlet.multipart.max-request-size=50MB

# AI Service
ai.service.url=http://localhost:5000
ai.service.analyze-endpoint=/analyze
```

### Python Configuration

Edit `app/main.py` to:
- Change port (default: 5000)
- Modify model selection
- Adjust risk analysis thresholds
- Add more clause types

## 🐛 Troubleshooting

### Issue: "Connection refused" when accessing frontend

**Solution**: 
- Ensure frontend server is running on correct port
- Check firewall settings
- Try accessing from same machine first

### Issue: AI service takes long to start

**Solution**:
- First run downloads models (~4GB) - this is normal
- Subsequent runs will be faster
- Ensure you have stable internet connection
- Check available disk space (10GB+ recommended)

### Issue: "Out of memory" error

**Solution**:
- Increase JVM heap size for Spring Boot:
  ```bash
  export MAVEN_OPTS="-Xmx4g"
  mvn spring-boot:run
  ```
- Close other applications to free up RAM
- Reduce document size

### Issue: PDF/DOCX file not parsing

**Solution**:
- Ensure file is not corrupted
- Try converting to PDF if DOCX
- Check file size (max 50MB)
- Verify file format is actually PDF/DOCX

### Issue: Analysis returns only "No risks" or empty results

**Solution**:
- This is normal for some documents
- Try with sample documents first
- Check document is in English
- Ensure document has sufficient content

### Issue: CORS errors in browser console

**Solution**:
- CORS is enabled by default
- Check that backend is running on http://localhost:8080
- Check that frontend is accessing correct backend URL
- Verify no firewall blocking requests

## 📈 Performance & Optimization

### Processing Time

- First run: 2-5 minutes (models loading)
- Subsequent runs: 30-60 seconds per document
- Depends on:
  - Document length (max 65k characters processed)
  - System RAM and CPU
  - GPU availability (if CUDA enabled)

### Optimization Tips

1. **GPU Support** (if available):
   - Install CUDA and cuDNN
   - Install `torch` with CUDA: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
   - Models will auto-use GPU if available

2. **Memory Optimization**:
   - Use SSD for faster model loading
   - Allocate sufficient RAM (8GB+ recommended)
   - Close unnecessary applications

3. **Chunking Large Documents**:
   - Documents > 65k characters are auto-chunked
   - Optimal: 10k-50k character documents

## 🔐 Security Considerations

1. **Confidentiality**: Use HTTPS for production
2. **Data Privacy**: Documents are processed in-memory only
3. **Authentication**: Add JWT for production deployment
4. **Input Validation**: File type and size validated
5. **Non-Compete Clauses**: Honored as per deployment rules

## 🚀 Future Enhancements

### Planned Features

1. **Multilingual Support**
   - Hindi language models
   - Regional language support

2. **Advanced NLP**
   - Legal Question Answering ("What happens if I break this?")
   - Outcome Prediction
   - Smart Contract analysis

3. **Integration**
   - Contract Lifecycle Management (CLM) system integration
   - Cloud deployment (AWS/Azure)
   - Database storage of analyses

4. **UI Enhancements**
   - Clause highlighting in original document
   - Side-by-side comparison
   - Batch upload functionality

5. **Legal Features**
   - Legal template suggestions
   - Compliance checking
   - Jurisdiction-specific analysis

## 📚 Research & Datasets

This project uses concepts from:

- **CUAD Dataset**: Contract Understanding Atticus Dataset
- **LexGLUE**: Legal Language Understanding Evaluation benchmark
- **ContractNLI**: For contract inference tasks
- **LegalBERT**: Legal domain understanding models
- **Longformer**: For long document processing (16k+ tokens)

## 📝 License & Disclaimer

This tool is provided for **information purposes only**. It is NOT a substitute for professional legal advice. Always consult with a qualified legal professional before making decisions based on this analysis.

## 👥 Contributing

Contributions are welcome! Please feel free to submit pull requests for:
- Bug fixes
- New features
- Documentation improvements
- Performance optimizations

## 📞 Support

For issues and questions:
1. Check troubleshooting section
2. Review API documentation in `/api/documents/docs`
3. Test with sample documents first
4. Check console logs for detailed error messages

---

**Last Updated**: March 2024
**Version**: 1.0.0
**Status**: Production Ready
