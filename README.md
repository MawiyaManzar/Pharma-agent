# Pharma Agentic AI - Drug Repurposing Intelligence Platform

An AI-powered multi-agent system for discovering drug repurposing opportunities by analyzing market data, clinical trials, patents, and scientific literature.

**Version**: 0.1.0  
**Status**: Production Ready  
**Demo Duration**: 4 minutes

## Architecture

### System Architecture
- **Backend**: FastAPI server with `/chats` endpoint
- **Frontend**: Streamlit web application
- **Orchestration**: LangGraph for multi-agent workflows

### Agent System

This system uses **LangGraph** to orchestrate multiple specialized agents:

- **Master Agent**: Orchestrates workflow and synthesizes results
- **IQVIA Insights Agent**: Market analysis and competition
- **EXIM Trade Agent**: Import/export and formulation data
- **Patent Landscape Agent**: Patent search and FTO analysis
- **Clinical Trials Agent**: Trial data from ClinicalTrials.gov/WHO ICTRP
- **Internal Insights Agent**: Internal document analysis
- **Web Intelligence Agent**: Scientific publications and guidelines
- **Report Generator Agent**: PDF/Excel report generation

### API Endpoints

- `POST /chats` - Main endpoint for processing molecule repurposing queries
- `GET /health` - Health check endpoint
- `GET /` - API information

## Quick Start

### Prerequisites
- Python 3.13+
- Google GenAI API key
- `uv` package manager (recommended) or `pip`

### Setup with uv (Recommended)

1. **Create virtual environment and install dependencies**:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

2. **Configure environment variables**:
Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_google_api_key_here
API_URL=http://localhost:8000
```

3. **Start the backend** (Terminal 1):
```bash
uvicorn src.api.main:app --reload --port 8000
```

4. **Start the frontend** (Terminal 2):
```bash
streamlit run src/ui/app.py
```

5. **Access the application**:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Setup with pip

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Follow steps 2-5 above**

## Project Structure

```
.
├── src/
│   ├── api/             # FastAPI backend application
│   │   └── main.py      # Main API with /chats endpoint
│   ├── agents/          # Agent implementations
│   ├── tools/           # Data source tools/mocks
│   ├── workflows/       # LangGraph workflow definitions
│   ├── reports/         # Report generation logic
│   └── ui/              # Streamlit frontend
│       └── app.py       # Main Streamlit application
├── tests/               # Test files
├── data/                # Mock data and fixtures
├── outputs/             # Generated reports
└── requirements.txt
```

## Usage

### Basic Usage

1. **Enter a molecule name** in the sidebar (e.g., "Metformin")
2. **Type your query** in the chat input (e.g., "Analyze Metformin for repurposing opportunities")
3. **Wait for analysis** - The system will:
   - Orchestrate 6 specialized agents
   - Gather intelligence from multiple domains
   - Synthesize results
   - Generate reports
4. **Review results** - View synthesis, key findings, and recommendations
5. **Download reports** - Get PDF and Excel reports with full analysis

### Example Queries

- "Analyze Metformin for repurposing opportunities"
- "What are the market opportunities for Aspirin?"
- "Assess Sildenafil for new indications"
- "Evaluate Ibuprofen for cardiovascular repurposing"

### API Usage

#### POST /chats
```bash
curl -X POST "http://localhost:8000/chats" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze Metformin for repurposing opportunities",
    "molecule": "Metformin",
    "session_id": "optional-session-id"
  }'
```

#### Download Reports
```bash
# Download PDF
curl -O "http://localhost:8000/reports/pdf/Metformin_Repurposing_Report_20241201_143022.pdf"

# Download Excel
curl -O "http://localhost:8000/reports/excel/Metformin_Repurposing_Report_20241201_143022.xlsx"
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_tools.py -v
pytest tests/test_agents.py -v
pytest tests/test_workflow.py -v
pytest tests/test_reports.py -v
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

- **Tools**: 15 tests ✅
- **Agents**: 16 tests ✅
- **Workflow**: 8 tests ✅
- **Reports**: 6 tests ✅
- **Integration**: 9 tests ✅
- **Total**: 54 tests, all passing ✅

### Code Quality

```bash
# Check linting
pylint src/

# Format code (if using black)
black src/ tests/
```

## Project Structure

```
.
├── src/
│   ├── api/                 # FastAPI backend
│   │   └── main.py          # API endpoints
│   ├── agents/              # Worker agents
│   │   ├── base_agent.py    # Base agent class
│   │   ├── iqvia_agent.py   # Market intelligence agent
│   │   ├── exim_agent.py    # Trade intelligence agent
│   │   ├── patent_agent.py  # Patent analysis agent
│   │   ├── clinical_trials_agent.py  # Clinical trials agent
│   │   ├── internal_insights_agent.py # Internal docs agent
│   │   └── web_intelligence_agent.py  # Web search agent
│   ├── tools/               # Mock data tools
│   │   ├── iqvia_tool.py    # Market data tool
│   │   ├── exim_tool.py     # Trade data tool
│   │   ├── patent_tool.py   # Patent data tool
│   │   ├── clinical_trials_tool.py  # Trial data tool
│   │   ├── internal_insights_tool.py # Internal docs tool
│   │   └── web_intelligence_tool.py  # Web search tool
│   ├── workflows/           # LangGraph workflows
│   │   ├── workflow.py      # Main workflow
│   │   ├── state.py         # State schema
│   │   └── master_agent.py  # Master agent
│   ├── reports/             # Report generation
│   │   └── report_generator.py  # PDF/Excel generator
│   └── ui/                  # Streamlit frontend
│       └── app.py           # Main UI
├── tests/                   # Test suite
│   ├── test_tools.py        # Tool tests
│   ├── test_agents.py       # Agent tests
│   ├── test_workflow.py     # Workflow tests
│   ├── test_reports.py      # Report tests
│   └── test_integration.py # Integration tests
├── outputs/                 # Generated reports
├── data/                    # Mock data (if any)
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── ARCHITECTURE.md         # Architecture documentation
├── demo_script.md          # Demo script
└── INTEGRATION_TESTING.md  # Testing guide
```

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[demo_script.md](demo_script.md)** - Demo script and guide
- **[INTEGRATION_TESTING.md](INTEGRATION_TESTING.md)** - Testing documentation

## Features

### Multi-Agent System
- **Master Agent**: Orchestrates workflow and synthesizes results
- **6 Worker Agents**: Specialized analysts for different domains
- **LangGraph Orchestration**: State machine for workflow management

### Intelligence Domains
- **Market Intelligence**: Market size, competition, growth (IQVIA)
- **Trade Intelligence**: Import/export, supply chain (EXIM)
- **Patent Intelligence**: Patent landscape, FTO analysis
- **Clinical Intelligence**: Trial data, emerging indications
- **Internal Intelligence**: Strategy documents, field insights
- **Web Intelligence**: Scientific publications, guidelines

### Report Generation
- **PDF Reports**: Professional multi-page reports
- **Excel Reports**: Structured multi-sheet workbooks
- **Automatic Generation**: Reports created after analysis

### User Interface
- **Streamlit Web UI**: Chat interface for queries
- **Progress Indicators**: Real-time workflow status
- **Results Display**: Synthesis, findings, recommendations
- **Report Downloads**: Direct download buttons

## Performance

- **Workflow Execution**: 1-3 minutes (with real LLM calls)
- **Report Generation**: 5-10 seconds
- **Total End-to-End**: 2-4 minutes

## Limitations

- **Mock Data**: All data sources are mocked for demo purposes
- **Sequential Execution**: Agents run sequentially (not parallel)
- **Single User**: Not optimized for concurrent users

## Future Enhancements

- Real API integrations (IQVIA, EXIM, etc.)
- Parallel agent execution
- Database for state persistence
- Caching for repeated queries
- User authentication
- Multi-user support

## Troubleshooting

### 500 Internal Server Error from Backend

**Root Cause**: Missing Python dependencies (most commonly `langgraph`, `fastapi`, or other packages from `requirements.txt`)

**Solution**:
1. **Run the diagnostic script**:
   ```bash
   python check_setup.py
   ```
   This will identify missing dependencies and configuration issues.

2. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check backend health endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```
   The health endpoint will show detailed information about missing dependencies or configuration issues.

4. **Check backend logs**: Look at the terminal where you started the backend (`uvicorn src.api.main:app --reload --port 8000`) for detailed error messages.

### Backend won't start
- Check if port 8000 is available: `lsof -i :8000` or `netstat -an | grep 8000`
- Verify GOOGLE_API_KEY is set in .env
- Check virtual environment is activated
- Verify all dependencies are installed: `pip list | grep langgraph`

### Frontend can't connect
- Verify backend is running on port 8000: `curl http://localhost:8000/health`
- Check API_URL in environment (should be `http://localhost:8000`)
- Verify CORS settings (should be configured to allow all origins in development)

### Workflow errors
- Check GOOGLE_API_KEY is valid and has proper permissions
- Verify all dependencies are installed: `python check_setup.py`
- Check logs for specific error messages
- Ensure .env file exists with GOOGLE_API_KEY

### Report generation fails
- Verify outputs/ directory exists: `mkdir -p outputs`
- Check file permissions
- Verify reportlab and openpyxl are installed: `pip list | grep -E "reportlab|openpyxl"`

## Contributing

This is an internal project. For contributions, please contact the project maintainer.

## License

Proprietary - Internal Use Only

## Support

For issues or questions, please refer to:
- Architecture documentation: `ARCHITECTURE.md`
- Testing guide: `INTEGRATION_TESTING.md`
- Demo script: `demo_script.md`

