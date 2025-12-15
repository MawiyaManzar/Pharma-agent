# API Documentation

## FastAPI Backend API

### Base URL
```
http://localhost:8000
```

## Endpoints

### GET /

**Description**: API information endpoint

**Response**:
```json
{
  "message": "Pharma Agentic AI API",
  "version": "0.1.0",
  "endpoints": {
    "chats": "/chats"
  }
}
```

---

### GET /health

**Description**: Health check endpoint

**Response**:
```json
{
  "status": "healthy"
}
```

---

### POST /chats

**Description**: Main endpoint for processing molecule repurposing queries

**Request Body**:
```json
{
  "message": "Analyze Metformin for repurposing opportunities",
  "molecule": "Metformin",
  "session_id": "optional-session-id"
}
```

**Parameters**:
- `message` (string, required): User query/question
- `molecule` (string, optional): Molecule name (can be extracted from message)
- `session_id` (string, optional): Session identifier for tracking

**Response** (200 OK):
```json
{
  "response": "Synthesized analysis text...",
  "status": "completed",
  "session_id": "session-id",
  "data": {
    "molecule": "Metformin",
    "synthesis": "Full synthesis text...",
    "key_findings": [
      "Finding 1",
      "Finding 2"
    ],
    "recommendations": [
      "Recommendation 1",
      "Recommendation 2"
    ],
    "summary": {
      "total_agents_executed": 6,
      "agents_failed": 0,
      "key_insights_count": 10,
      "recommendations_count": 8
    }
  },
  "report_paths": {
    "pdf": "outputs/Metformin_Repurposing_Report_20241201_143022.pdf",
    "excel": "outputs/Metformin_Repurposing_Report_20241201_143022.xlsx",
    "base_filename": "Metformin_Repurposing_Report_20241201_143022"
  },
  "workflow_state": {
    "agents_completed": ["iqvia", "exim", "patent", "clinical_trials", "internal", "web"],
    "agents_failed": [],
    "current_step": "completed"
  }
}
```

**Response Codes**:
- `200`: Success
- `500`: Internal server error
- `422`: Validation error

**Example**:
```bash
curl -X POST "http://localhost:8000/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze Metformin for repurposing opportunities",
    "molecule": "Metformin"
  }'
```

---

### GET /reports/{type}/{filename}

**Description**: Download generated report files

**Parameters**:
- `type` (path parameter): Report type - `pdf` or `excel`
- `filename` (path parameter): Name of the report file

**Response**:
- `200`: File download
- `400`: Invalid report type
- `404`: Report not found

**Example**:
```bash
# Download PDF
curl -O "http://localhost:8000/reports/pdf/Metformin_Repurposing_Report_20241201_143022.pdf"

# Download Excel
curl -O "http://localhost:8000/reports/excel/Metformin_Repurposing_Report_20241201_143022.xlsx"
```

**Security**:
- Path traversal prevention
- Only `pdf` and `excel` types allowed
- Files must exist in `outputs/` directory

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid report type"
}
```

### 404 Not Found
```json
{
  "detail": "Report not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error processing request: <error message>"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider:
- Per-IP rate limiting
- Per-user rate limiting
- Request queuing for long-running operations

---

## Authentication

Currently no authentication is required. For production, consider:
- API key authentication
- OAuth 2.0
- JWT tokens

---

## Timeouts

- Request timeout: 600 seconds (10 minutes)
- LLM API calls: Varies (typically 30-60 seconds per agent)
- Total workflow: 1-3 minutes typical

---

## CORS

CORS is enabled for all origins (`*`). For production, specify exact origins:
```python
allow_origins=["http://localhost:8501", "https://yourdomain.com"]
```




