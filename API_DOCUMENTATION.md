# 🔌 API Documentation

Complete API reference for Legal Document Analyzer

## Base URLs

- **Backend API**: `http://localhost:8080/api`
- **AI Service**: `http://localhost:5000`

---

## Backend APIs (Spring Boot)

### 1. Upload and Analyze Document

**Endpoint**: `POST /documents/analyze`

**Base URL**: `http://localhost:8080/api/documents/analyze`

**Description**: Upload a legal document (PDF or DOCX) for complete analysis

**Request**:
- **Content-Type**: multipart/form-data
- **Parameter Name**: file
- **File Types**: PDF, DOCX
- **Max Size**: 50MB

**Example - cURL**:
```bash
curl -X POST http://localhost:8080/api/documents/analyze \
  -F "file=@rental-agreement.pdf"
```

**Example - JavaScript Fetch**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8080/api/documents/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Example - Python Requests**:
```python
import requests

files = {'file': open('rental-agreement.pdf', 'rb')}
response = requests.post(
    'http://localhost:8080/api/documents/analyze',
    files=files
)
print(response.json())
```

**Response**: `200 OK`
```json
{
  "fileName": "rental-agreement.pdf",
  "originalText": "This Agreement made this 15th day...",
  "summary": "This is a residential lease agreement...",
  "simplified_text": "The landlord agrees to rent...",
  "key_clauses": [
    {
      "type": "liability",
      "text": "The Landlord shall not be liable...",
      "section": "Section 5",
      "severity_level": "high",
      "confidence": 0.85,
      "explanation": "Liability limitation clause detected",
      "is_risky": false
    }
  ],
  "risks": [
    {
      "type": "high_penalty",
      "description": "High penalties found in document",
      "severity_level": "high",
      "affected_clause": "Late payment penalty of Rs. 500/- per day",
      "recommendation": "Negotiate lower penalty amount",
      "clause": "Late payment of rent shall attract a penalty..."
    }
  ],
  "pros": [
    "✓ Warranty provided",
    "✓ Termination at will"
  ],
  "cons": [
    "✗ Non-refundable deposit",
    "✗ High penalties"
  ],
  "extracted_entities": {
    "parties": ["Rajesh Kumar", "Amit Patel"],
    "dates": ["15th day of January, 2024"],
    "amounts": ["Rs. 45,000/-", "Rs. 1,35,000/-"],
    "locations": [],
    "sections_found": 10
  },
  "analysis_timestamp": 1708000000000,
  "document_length": 8764,
  "status": "completed",
  "error": null
}
```

**Error Response**: `500 Internal Server Error`
```json
{
  "error": "File processing failed: Invalid PDF",
  "status": "failed"
}
```

---

### 2. Health Check

**Endpoint**: `GET /documents/health`

**Base URL**: `http://localhost:8080/api/documents/health`

**Description**: Check if backend service is running

**Request**: No parameters needed

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "service": "Legal Document Analyzer API",
  "version": "1.0.0"
}
```

---

### 3. API Documentation

**Endpoint**: `GET /documents/docs`

**Base URL**: `http://localhost:8080/api/documents/docs`

**Description**: Get API documentation

**Response**: `200 OK`
```json
{
  "title": "Legal Document Analyzer API",
  "version": "1.0.0",
  "endpoints": {
    "analyze": {
      "method": "POST",
      "path": "/api/documents/analyze",
      "description": "Upload and analyze a legal document",
      "parameters": {
        "file": "MultipartFile (PDF or DOCX)"
      }
    }
  }
}
```

---

## AI Service APIs (Python Flask)

### 1. Complete Analysis

**Endpoint**: `POST /analyze`

**Base URL**: `http://localhost:5000/analyze`

**Description**: Perform complete analysis on document text

**Request**:
```json
{
  "text": "Complete legal document text here..."
}
```

**Example - cURL**:
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "RENTAL AGREEMENT between Landlord and Tenant..."
  }'
```

**Response**: `200 OK`
```json
{
  "summary": "This is a rental agreement...",
  "simplified_text": "The agreement specifies rent payment...",
  "key_clauses": [
    {
      "type": "payment",
      "text": "Monthly rent of Rs. 45,000...",
      "section": "Section 1",
      "severity_level": "medium",
      "confidence": 0.78,
      "explanation": "Payment clause clause detected",
      "is_risky": false
    }
  ],
  "risks": [
    {
      "type": "missing_termination_clause",
      "description": "No termination clause found in document",
      "severity_level": "critical",
      "affected_clause": "N/A",
      "recommendation": "Add clear termination conditions including notice period",
      "clause": "Missing"
    }
  ],
  "extracted_entities": {
    "parties": ["Landlord Name", "Tenant Name"],
    "dates": ["15th day of January, 2024"],
    "amounts": ["Rs. 45,000/-"],
    "locations": [],
    "sections_found": 10
  },
  "pros": ["✓ Termination at will"],
  "cons": ["✗ High penalties"]
}
```

---

### 2. Extract Entities

**Endpoint**: `POST /extract-entities`

**Base URL**: `http://localhost:5000/extract-entities`

**Description**: Extract parties, dates, amounts, and locations

**Request**:
```json
{
  "text": "Legal document text..."
}
```

**Response**: `200 OK`
```json
{
  "parties": ["Party 1 Name", "Party 2 Name"],
  "dates": ["15th January 2024", "31st December 2024"],
  "amounts": ["Rs. 50,00,000", "Rs. 1,35,000"],
  "locations": [],
  "sections_found": 10
}
```

---

### 3. Classify Clauses

**Endpoint**: `POST /classify-clauses`

**Base URL**: `http://localhost:5000/classify-clauses`

**Description**: Identify and classify legal clauses

**Request**:
```json
{
  "text": "Legal document text..."
}
```

**Response**: `200 OK`
```json
{
  "key_clauses": [
    {
      "type": "liability",
      "text": "Neither party shall be liable for...",
      "section": "Section 5",
      "severity_level": "high",
      "confidence": 0.87,
      "explanation": "Liability limitation detected",
      "is_risky": true
    },
    {
      "type": "termination",
      "text": "This agreement may be terminated by...",
      "section": "Section 6",
      "severity_level": "medium",
      "confidence": 0.92,
      "explanation": "Termination clause detected",
      "is_risky": false
    }
  ]
}
```

---

### 4. Summarize Document

**Endpoint**: `POST /summarize`

**Base URL**: `http://localhost:5000/summarize`

**Description**: Generate abstractive summary

**Request**:
```json
{
  "text": "Long legal document text..."
}
```

**Response**: `200 OK`
```json
{
  "summary": "This rental agreement between Rajesh Kumar (Landlord) and Amit Patel (Tenant) specifies a monthly rent of Rs. 45,000 with security deposit of Rs. 1,35,000. The lease term is from February 1, 2024 to January 31, 2025, with 60 days notice for termination."
}
```

---

### 5. Simplify Text

**Endpoint**: `POST /simplify`

**Base URL**: `http://localhost:5000/simplify`

**Description**: Convert legal jargon to plain English

**Request**:
```json
{
  "text": "The Landlord hereby lets to the Tenant and the Tenant hereby hires from the Landlord..."
}
```

**Response**: `200 OK`
```json
{
  "simplified_text": "The Landlord agrees to rent to the Tenant and the Tenant agrees to rent from the Landlord. The agreement specifies conditions and terms for the rental. Neither party shall be liable for damages caused by the other party's negligence or breach of this agreement..."
}
```

---

### 6. Risk Analysis

**Endpoint**: `POST /risk-analysis`

**Base URL**: `http://localhost:5000/risk-analysis`

**Description**: Analyze risks and extract pros/cons

**Request**:
```json
{
  "text": "Legal document text..."
}
```

**Response**: `200 OK`
```json
{
  "risks": [
    {
      "type": "missing_termination_clause",
      "description": "No clear termination clause found",
      "severity_level": "critical",
      "affected_clause": "N/A",
      "recommendation": "Add explicit termination conditions",
      "clause": "Missing"
    },
    {
      "type": "high_penalty",
      "description": "High penalties detected",
      "severity_level": "high",
      "affected_clause": "Rs. 500 per day penalty",
      "recommendation": "Negotiate lower penalty rates",
      "clause": "Late payment of rent shall attract a penalty of Rs. 500/- per day"
    }
  ],
  "pros": [
    "✓ Clear payment terms",
    "✓ Defined notice period for termination",
    "✓ Maintenance responsibilities specified"
  ],
  "cons": [
    "✗ High daily penalties",
    "✗ Landlord not liable for any damages",
    "✗ Limited termination rights for tenant"
  ]
}
```

---

### 7. Test Endpoint (Sample Analysis)

**Endpoint**: `GET /test`

**Base URL**: `http://localhost:5000/test`

**Description**: Test the service with a pre-configured sample document

**Response**: `200 OK`
```json
{
  "summary": "Sample analysis output...",
  "simplified_text": "Sample simplified text...",
  "key_clauses": [...],
  "risks": [...],
  "pros": [...],
  "cons": [...]
}
```

---

### 8. Health Check

**Endpoint**: `GET /health`

**Base URL**: `http://localhost:5000/health`

**Description**: Check if AI service is running

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "service": "Legal Document Analyzer AI Service",
  "version": "1.0.0",
  "timestamp": "2024-02-15T10:30:00"
}
```

---

## Response Models

### AnalysisResponse

Main response object from backend:

```typescript
{
  fileName: string;                    // Original filename
  originalText: string;                // Full extracted text
  summary: string;                     // TL;DR summary
  simplified_text: string;             // Simplified version
  key_clauses: KeyClause[];            // Identified clauses
  risks: Risk[];                       // Identified risks
  pros: string[];                      // Favorable terms
  cons: string[];                      // Unfavorable terms
  extracted_entities: {
    parties: string[];
    dates: string[];
    amounts: string[];
    locations: string[];
    sections_found: number;
  };
  analysis_timestamp: number;          // Unix timestamp
  document_length: number;             // Character count
  status: string;                      // "completed" or "failed"
  error: string | null;                // Error message if any
}
```

### KeyClause

Individual clause object:

```typescript
{
  type: string;                        // "liability", "termination", etc.
  text: string;                        // Clause text (truncated)
  section: string;                     // Section number
  severity_level: string;              // "high", "medium", "low"
  confidence: number;                  // 0.0 to 1.0
  explanation: string;                 // Why it's classified this way
  is_risky: boolean;                   // Risky flag
}
```

### Risk

Individual risk object:

```typescript
{
  type: string;                        // Risk type
  description: string;                 // What the risk is
  severity_level: string;              // "critical", "high", "medium", "low"
  affected_clause: string;             // Problematic text
  recommendation: string;              // How to mitigate
  clause: string;                      // Full clause text
}
```

---

## Error Handling

### Common Error Responses

**400 Bad Request** - Invalid input
```json
{
  "error": "Only PDF and DOCX files are supported"
}
```

**413 Payload Too Large** - File exceeds limit
```json
{
  "error": "File size exceeds 50MB limit"
}
```

**500 Internal Server Error**
```json
{
  "error": "Analysis failed: Service temporarily unavailable"
}
```

---

## Clause Types

Recognized clause types:

- `liability` - Limitation of liability
- `termination` - Termination conditions
- `penalty` - Penalties and fines
- `indemnification` - Indemnification clauses
- `confidentiality` - Confidentiality/NDA
- `dispute_resolution` - Dispute handling
- `payment` - Payment terms
- `governing_law` - Applicable law
- `default` - Default conditions

---

## Risk Types

Identified risk types:

- `high_penalty` - Unusually high penalties detected
- `one_sided` - Heavily one-sided terms
- `missing_clause` - Critical clause is missing
- `missing_termination_clause` - No termination conditions
- `unusual_clause` - Non-standard or risky terms
- `ambiguous_terms` - Vague or subjective language

---

## Severity Levels

Risk severity classifications:

| Level | Meaning |
|-------|---------|
| `critical` | Immediate attention required |
| `high` | Should be reviewed and negotiated |
| `medium` | Consider for negotiation |
| `low` | Minor, but should be aware |

---

## Rate Limiting & Quotas

- No rate limiting implemented for local deployment
- For production, add authentication and rate limiting

---

## Examples

### Complete Workflow in Python

```python
import requests
import json

# Read document
with open('rental-agreement.txt', 'r') as f:
    text = f.read()

# 1. Extract entities
entities = requests.post(
    'http://localhost:5000/extract-entities',
    json={'text': text}
).json()

print("Parties:", entities['parties'])
print("Dates:", entities['dates'])

# 2. Analyze risks
risks = requests.post(
    'http://localhost:5000/risk-analysis',
    json={'text': text}
).json()

print("Critical Risks:")
for risk in risks['risks']:
    if risk['severity_level'] == 'critical':
        print(f"- {risk['description']}")

# 3. Get summary
summary = requests.post(
    'http://localhost:5000/summarize',
    json={'text': text}
).json()

print("Summary:", summary['summary'])
```

### Complete Workflow in JavaScript

```javascript
// Upload file through REST API
const file = document.getElementById('fileInput').files[0];
const formData = new FormData();
formData.append('file', file);

fetch('http://localhost:8080/api/documents/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Summary:', data.summary);
  console.log('Risks:', data.risks);
  console.log('Clauses:', data.key_clauses);
});
```

---

For more information, see README.md
