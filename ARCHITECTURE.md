# 📐 Architecture & Technical Design

Complete technical architecture and design decisions for Legal Document Analyzer

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  HTML/CSS/JavaScript Frontend (localhost:3000)           │   │
│  │  - File upload interface                                 │   │
│  │  - Results visualization                                 │   │
│  │  - Document analysis display                             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
                    HTTP/REST (AJAX/Fetch)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌─────────────────────────────┐    ┌──────────────────────────────┐
│   SPRING BOOT BACKEND       │    │    PYTHON AI SERVICE         │
│  (localhost:8080/api)       │    │   (localhost:5000)           │
│ ┌───────────────────────┐   │    │ ┌────────────────────────┐   │
│ │ REST API Controller   │   │    │ │ Flask Application      │   │
│ │ - /documents/analyze  │   │    │ │ - NLP Pipeline         │   │
│ │ - /documents/health   │   │    │ │ - Model Management     │   │
│ ├───────────────────────┤   │    │ ├────────────────────────┤   │
│ │ Service Layer         │   │    │ │ NLP Components         │   │
│ │ - DocumentAnalysis    │───┼────┼─→ 1. Entity Extraction  │   │
│ │ - File Processing     │   │    │ 2. Clause Classification│   │
│ ├───────────────────────┤   │    │ 3. Summarization       │   │
│ │ Utility Layer         │   │    │ 4. Simplification      │   │
│ │ - DocumentParser      │   │    │ 5. Risk Analysis       │   │
│ │ - AIServiceClient     │   │    │ ├────────────────────────┤   │
│ │ ├─ PDF/DOCX Parsing   │   │    │ │ HuggingFace Models     │   │
│ │ ├─ HTTP Communication │   │    │ │ - BART (summarization) │   │
│ │ └─ Text Chunking      │   │    │ │ - RoBERTa (classification)
│ └───────────────────────┘   │    │ │ - GPT2 (generation)    │   │
└─────────────────────────────┘    │ │ - Custom Rules         │   │
                                  │ └────────────────────────┘   │
                                  └──────────────────────────────┘
```

## Technology Stack

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| HTML | HTML5 | Document structure |
| Styling | CSS3 | Responsive design |
| JavaScript | Vanilla ES6+ | Client-side logic, API calls |
| HTTP | Fetch API | Backend communication |

### Backend (Spring Boot)
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Spring Boot 3.2 | REST APIs, MVC |
| Language | Java 17 | Type-safe backend |
| Build Tool | Maven 3.8 | Dependency management |
| PDF Parsing | Apache PDFBox | Extract text from PDFs |
| DOCX Parsing | Apache POI | Extract text from DOCX |
| HTTP Client | Apache HttpClient5 | Call AI service |
| JSON Processing | Jackson | JSON serialization |
| Logging | SLF4J | Logging framework |

### AI Service (Python)
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Flask 3.0 | REST API server |
| NLP Library | Transformers 4.36 | Pre-trained models |
| DL Framework | PyTorch 2.1 | Deep learning |
| Summarization | BART-Large-CNN | Abstractive summarization |
| Classification | BART-Large-MNLI | Zero-shot classification |
| Text Generation | GPT2 | Text generation for simplification |
| Tokenization | Sentence Piece | Token processing |
| Environment | Conda/venv | Virtual environment |

---

## Data Flow

### 1. File Upload Flow

```
User uploads file (PDF/DOCX)
    ↓
Browser (JavaScript)
    ↓ Multipart/form-data
Spring Boot Controller
    ↓
DocumentParser (Apache PDFBox/POI)
    ↓ Extract raw text
DocumentAnalysisService
    ↓ Process text (chunk if needed)
AIServiceClient
    ↓ HTTP POST JSON
Python Flask App
    ↓
NLP Pipeline (5 stages)
    ↓ Return JSON results
Spring Boot
    ↓ HTML Response
Browser (JavaScript)
    ↓
Display results with visualization
```

### 2. Analysis Pipeline Flow

```
Raw Text Input
    ↓
Stage 1: Information Extraction
├─ Party extraction (Named Entity Recognition)
├─ Date extraction (Regex + patterns)
├─ Amount extraction (Currency pattern matching)
└─ Section counting
    ↓
Stage 2: Clause Classification
├─ Text chunking (1024 chars per chunk)
├─ Zero-shot classification (BART-MNLI)
├─ Confidence scoring
└─ Severity assessment
    ↓
Stage 3: Summarization
├─ Document chunking
├─ BART abstractive summarization
├─ Summary generation
└─ TL;DR output
    ↓
Stage 4: Simplification
├─ Legal jargon replacement (rule-based)
├─ Sentence restructuring
└─ Plain English output
    ↓
Stage 5: Risk Analysis
├─ Pattern matching for risks
├─ Missing clause detection
├─ Severity classification
└─ Recommendation generation
    ↓
Combined Output JSON
```

---

## API Contract

### Request Flow

```
Frontend HTTP Request
    ↓
Spring Boot Receives
    |- Validate file (type, size)
    |- Parse document (PDF/DOCX → Text)
    ↓
AI Service Request
    |- Send chunked text
    |- Wait for response
    ↓
Python Service Processes
    |- Run all 5 NLP stages
    |- Generate JSON response
    ↓
Spring Boot Receives AI Response
    |- Check for errors
    |- Parse JSON response
    |- Enhance results (optional)
    ↓
Return to Frontend
    |- Send complete analysis JSON
    ↓
Frontend Displays
    |- Parse JSON
    |- Render results
    |- Show visualizations
```

---

## Model Architecture

### Information Extraction
```
Legal Document Text
    ↓
Regex/Pattern Matching Rules
    ├─ Party: "Between [Name] and [Name]"
    ├─ Dates: \d{1,2}[-/]\d{1,2}[-/]\d{4}
    ├─ Amounts: Rs\.?\s*[\d,]+
    ├─ Locations: [City|Place] names
    └─ Sections: Count of sections
    ↓
Extracted Entities JSON
```

### Clause Classification
```
Clause Text (0-500 chars)
    ↓
BART-Large-MNLI (Zero-shot classifier)
    ├─ Labels: ["liability", "termination", "penalty", ...]
    ├─ Multi-class: False (single best match)
    └─ Max possible: 8 clause types
    ↓
Classification Output
    ├─ Type (highest confidence)
    ├─ Confidence score (0-1)
    ├─ Severity (based on confidence)
    └─ Risk flag (if risky clause)
```

### Summarization
```
Long Document (4k-65k chars)
    ↓
Chunking Module
    └─ Split into 1024-char chunks (with overlap)
    ↓
BART-Large-CNN (Abstractive Summarization)
    ├─ Input: First chunk (must be > 50 tokens)
    ├─ Max output: 100 tokens (~400 chars)
    ├─ Min output: 30 tokens (~120 chars)
    └─ Algorithm: Pre-trained on CNN/DailyMail
    ↓
Summary Output
```

### Simplification
```
Legal Document Text
    ↓
Jargon Replacement Dictionary
    ├─ "hereby" → "by this"
    ├─ "wheresoever" → "wherever"
    ├─ "indemnify" → "protect from harm"
    ├─ "amortized over" → "paid back over time"
    └─ [40+ rules for Indian legal terms]
    ↓
Simplified Output (plain English)
```

### Risk Analysis
```
Document Text
    ↓
Risk Pattern Matching Engine
    ├─ High Penalties: Rs\., ₹ amounts > 100k
    ├─ One-Sided: "one party", "only", "sole"
    ├─ Missing Clauses: Check for key terms
    ├─ Unusual Terms: "indefinite", "perpetual"
    └─ Ambiguous: "may", "should", "reasonable"
    ↓
Risk Scoring & Prioritization
    ├─ Critical Risks (missing termination)
    ├─ High Risks (high penalties)
    ├─ Medium Risks (one-sided terms)
    └─ Low Risks (minor issues)
    ↓
Risk Output with Recommendations
```

---

## Performance Characteristics

### Latency
| Operation | Time | Factor |
|-----------|------|--------|
| File Upload | <1s | Network + file size |
| PDF Parsing | 2-5s | File size, complexity |
| Entity Extraction | 1-2s | Document length |
| Clause Classification | 5-15s | Model loading + inference |
| Summarization | 10-20s | First run (model load) |
| Subsequent runs | 30-60s | Model inference only |

### Memory Usage
| Component | Usage | Notes |
|-----------|-------|-------|
| Frontend | 50MB | Loaded in browser |
| Spring Boot | 500MB-1GB | JVM heap |
| Python AI Service | 2-4GB | Transformer models loaded |
| BART Model | 1.6GB | Summarization model |
| MNLI Model | 900MB | Classification model |

### Scalability Considerations
1. **Horizontal Scaling**: Run multiple backend instances behind load balancer
2. **Queue System**: Add job queue for async processing
3. **Model Caching**: Cache models after first load
4. **GPU Support**: Enable CUDA for 10x speedup
5. **CDN**: Serve frontend through CDN

---

## Security Architecture

### Data Flow Security
```
Browser (CORS enabled)
    ↓ HTTPS/HTTP (local)
Spring Boot (Input validation)
    ├─ File type check (PDF/DOCX only)
    ├─ File size limit (50MB max)
    ├─ Virus scan (optional)
    └─ Text encoding validation
    ↓
Python AI Service (Local network)
    ├─ Input sanitization
    ├─ Text length limits
    └─ Rate limiting (optional)
    ↓
Processing (In-memory only)
    ├─ No persistent storage (default)
    ├─ Cleanup after processing
    └─ No data leakage
```

### Authentication & Authorization (Production)
```
Frontend
    ↓ User login
Spring Boot
    ├─ JWT token generation
    ├─ Token validation on each request
    └─ Role-based access control
AI Service
    └─ Authenticated requests only
```

---

## Extension Points

### 1. Custom Models
Replace models in `ai-service-python/app/main.py`:
```python
SUMMARIZATION_MODEL = "your-custom-model"
CLASSIFICATION_MODEL = "your-legal-bert-model"
```

### 2. Database Integration
Add entity classes and repositories:
```java
@Entity
public class Document {
    // Database persistence
}
```

### 3. Additional Clause Types
Extend `CLAUSE_TYPES` in Python AI service

### 4. Language Support
Add language detection and multilingual models:
```python
nlp = pipeline("zero-shot-classification", 
               model="xlm-roberta-base")
```

### 5. Custom Risk Rules
Modify `analyze_risks()` function to add domain-specific rules

---

## Testing Strategy

### Unit Tests
```java
// Spring Boot
@SpringBootTest
public class DocumentParserTest {
    @Test
    public void testPdfExtraction() { }
}
```

### Integration Tests
```python
# Flask
def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
```

### E2E Tests
- Upload sample document
- Verify all analyses complete
- Validate output format
- Check performance metrics

---

## Monitoring & Logging

### Logging Levels
| Level | Purpose |
|-------|---------|
| DEBUG | Development, detailed flow |
| INFO | Important events, status |
| WARN | Potential issues |
| ERROR | Failures requiring attention |

### Key Metrics to Monitor
- Avg processing time per document
- Success/failure rate
- Model load time
- Memory usage
- API response times
- Error rate by endpoint

---

## Deployment Options

### Local Development
- Single machine, all services local
- Best for: Testing, development

### Cloud Web Server
- Spring Boot on App Service/EC2
- Python on Container Instance
- Frontend on Static Hosting
- Best for: Small-medium teams

### Kubernetes
- Containerized services
- Auto-scaling capabilities
- Load balancing
- Best for: Production at scale

### Serverless
- Lambda/Cloud Functions for APIs
- Trigger-based processing
- Pay-per-use
- Best for: Sporadic usage

---

For specific implementation details, refer to source code and README.md
