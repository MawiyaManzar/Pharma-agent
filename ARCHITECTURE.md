# Pharma Agentic AI - Architecture Documentation

## System Overview

The Pharma Agentic AI platform is a multi-agent system designed to accelerate drug repurposing research. It uses a Master Agent to orchestrate multiple specialized Worker Agents, each responsible for analyzing a specific domain of pharmaceutical intelligence.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend                        │
│  (User Interface - Molecule Input, Results Display, Downloads)  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  /chats endpoint - Receives queries, orchestrates flow   │   │
│  │  /reports/{type}/{filename} - Serves generated reports  │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LangGraph Workflow Engine                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  DrugRepurposingWorkflow                                  │   │
│  │  - State Management                                        │   │
│  │  - Agent Orchestration                                     │   │
│  │  - Result Synthesis                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Master Agent                                │
│  - Query Analysis                                                │
│  - Task Breakdown                                                │
│  - Agent Routing                                                 │
│  - Result Synthesis                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Worker Agent 1│  │ Worker Agent 2│  │ Worker Agent N│
│  (IQVIA)      │  │  (EXIM)       │  │  (Web Intel)  │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   Tool 1      │  │   Tool 2     │  │   Tool N     │
│  (IQVIA API)  │  │  (EXIM API)  │  │  (Web Search)│
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Report Generator      │
                │  - PDF Generation      │
                │  - Excel Generation    │
                └───────────────────────┘
```

## Component Architecture

### 1. Frontend Layer (Streamlit)

**File**: `src/ui/app.py`

**Responsibilities**:
- User interface for molecule input
- Query submission to backend
- Progress indication during workflow execution
- Results display (synthesis, findings, recommendations)
- Report download functionality
- Error handling and user feedback

**Key Features**:
- Chat interface for natural language queries
- Real-time progress indicators
- Expandable sections for detailed information
- Download buttons for PDF and Excel reports
- Session state management

### 2. Backend Layer (FastAPI)

**File**: `src/api/main.py`

**Responsibilities**:
- RESTful API endpoints
- Request/response handling
- Workflow orchestration
- Report generation coordination
- File serving for downloads

**Endpoints**:
- `GET /` - API information
- `GET /health` - Health check
- `POST /chats` - Main analysis endpoint
- `GET /reports/{type}/{filename}` - Report download

**Key Features**:
- CORS middleware for frontend access
- Async request handling
- Error handling with proper HTTP status codes
- Security checks for file downloads

### 3. Workflow Layer (LangGraph)

**Files**: 
- `src/workflows/workflow.py` - Workflow definition
- `src/workflows/state.py` - State schema
- `src/workflows/master_agent.py` - Master Agent

**Responsibilities**:
- State machine management
- Agent orchestration
- Workflow execution control
- Error recovery

**Workflow Steps**:
1. **Plan**: Determine which agents to run
2. **Execute Agents**: Run worker agents (sequential)
   - Execute IQVIA Agent
   - Execute EXIM Agent
   - Execute Patent Agent
   - Execute Clinical Trials Agent
   - Execute Internal Agent
   - Execute Web Agent
3. **Synthesize**: Combine all agent results
4. **Complete**: Return final state

**State Schema**:
- Input: molecule, user_query, context
- Agent tracking: agents_to_run, agents_completed, agents_failed
- Results: Individual agent results (iqvia_result, exim_result, etc.)
- Synthesis: synthesized_result, report_data
- Control: current_step, error, messages

### 4. Agent Layer

**Files**: `src/agents/*.py`

**Master Agent** (`master_agent.py`):
- Orchestrates all worker agents
- Breaks down queries into tasks
- Routes tasks to appropriate agents
- Synthesizes results into strategic narrative

**Worker Agents** (6 specialized agents):
1. **IQVIA Insights Agent** - Market intelligence
2. **EXIM Trade Agent** - Trade and supply chain
3. **Patent Landscape Agent** - Patent and FTO analysis
4. **Clinical Trials Agent** - Clinical research
5. **Internal Insights Agent** - Internal documents
6. **Web Intelligence Agent** - Scientific literature

**Agent Structure**:
- Base class: `BaseWorkerAgent`
- Each agent: Specialized system prompt, tool integration, analysis method
- Output: Structured insights with key findings and recommendations

### 5. Tool Layer

**Files**: `src/tools/*.py`

**Mock Tools** (6 tools):
1. **IQVIA Tool** - Market data (size, competition, growth)
2. **EXIM Tool** - Trade data (import/export, supply chain)
3. **Patent Tool** - Patent data (landscape, FTO)
4. **Clinical Trials Tool** - Trial data (ongoing, completed)
5. **Internal Insights Tool** - Internal documents
6. **Web Intelligence Tool** - Web search results

**Tool Features**:
- LangChain-compatible (`@tool` decorator)
- Realistic mock data generation
- Structured output (string + raw data)
- Configurable parameters

### 6. Report Generation Layer

**File**: `src/reports/report_generator.py`

**Responsibilities**:
- PDF report generation (ReportLab)
- Excel report generation (openpyxl)
- Professional formatting
- Multi-section/multi-sheet organization

**Report Structure**:
- **PDF**: Title page, Executive Summary, Key Findings, Agent Results, Recommendations, Statistics
- **Excel**: Executive Summary, Key Findings, Recommendations, Agent Results, Statistics sheets

## Data Flow

### Request Flow

1. **User Input** → Streamlit UI
2. **HTTP Request** → FastAPI `/chats` endpoint
3. **Workflow Initialization** → LangGraph workflow
4. **Master Agent** → Determines agents to run
5. **Worker Agents** → Execute in sequence
   - Each agent calls its tool
   - Tool returns mock data
   - Agent analyzes with LLM
   - Agent returns structured insights
6. **Synthesis** → Master Agent combines all results
7. **Report Generation** → PDF and Excel created
8. **Response** → FastAPI returns results + report paths
9. **UI Display** → Streamlit shows results and download buttons

### State Flow

```
Initial State
    ↓
Planning State (determine agents)
    ↓
Execution State (run agents sequentially)
    ↓
Synthesis State (combine results)
    ↓
Completed State (reports generated)
```

## Technology Stack

### Core Framework
- **LangGraph**: Workflow orchestration and state management
- **LangChain**: Agent framework and tool integration
- **Google GenAI (Gemini)**: LLM for agent reasoning

### Backend
- **FastAPI**: REST API framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

### Frontend
- **Streamlit**: Web UI framework
- **Requests**: HTTP client

### Report Generation
- **ReportLab**: PDF generation
- **openpyxl**: Excel generation
- **Pandas**: Data manipulation

### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support

## Agent Roles and Responsibilities

### Master Agent
- **Role**: Senior Pharmaceutical Strategy Director
- **Responsibilities**:
  - Interpret user queries
  - Break down tasks
  - Route to worker agents
  - Synthesize results
  - Generate strategic recommendations

### Worker Agents

1. **IQVIA Insights Agent**
   - **Role**: Market Intelligence Analyst
   - **Focus**: Market size, competition, growth, therapy areas

2. **EXIM Trade Agent**
   - **Role**: Trade Intelligence Analyst
   - **Focus**: Import/export, supply chain, risk assessment

3. **Patent Landscape Agent**
   - **Role**: Patent Intelligence Analyst
   - **Focus**: Patent landscape, FTO analysis, expiry timelines

4. **Clinical Trials Agent**
   - **Role**: Clinical Research Analyst
   - **Focus**: Ongoing trials, phase distribution, emerging indications

5. **Internal Insights Agent**
   - **Role**: Strategic Intelligence Analyst
   - **Focus**: Internal documents, strategy alignment, priorities

6. **Web Intelligence Agent**
   - **Role**: Scientific Intelligence Analyst
   - **Focus**: Publications, guidelines, regulatory news

## Decision Logic

### Agent Selection
- Default: Run all 6 agents for comprehensive analysis
- Future: Query-based agent selection (e.g., "market only" → IQVIA only)

### Synthesis Logic
- Combines all agent analyses
- Identifies patterns across domains
- Highlights repurposing opportunities
- Provides strategic recommendations

### Error Handling
- Agent failures don't stop workflow
- Failed agents tracked in state
- Synthesis continues with successful agents
- Error messages included in response

## Scalability Considerations

### Current Limitations
- Sequential agent execution (not parallel)
- Single-threaded workflow execution
- Mock data (not real APIs)

### Future Enhancements
- Parallel agent execution
- Async workflow processing
- Real API integrations
- Caching for repeated queries
- Database for state persistence

## Security Considerations

### Current Implementation
- Path traversal prevention in file downloads
- CORS configuration for frontend access
- Environment variable for API keys

### Production Recommendations
- API key rotation
- Rate limiting
- Authentication/authorization
- Input validation and sanitization
- Secure file storage
- Audit logging

## Performance Characteristics

### Expected Timings
- Workflow execution: 1-3 minutes (with real LLM calls)
- Report generation: 5-10 seconds
- Total end-to-end: 2-4 minutes

### Bottlenecks
- LLM API calls (sequential)
- Report generation (I/O bound)
- Network latency (if using external APIs)

### Optimization Opportunities
- Parallel agent execution
- Caching LLM responses
- Async report generation
- Background job processing

## Deployment Architecture

### Development
- Local FastAPI server (port 8000)
- Local Streamlit app (port 8501)
- Local file storage (outputs/)

### Production Recommendations
- Containerized deployment (Docker)
- Reverse proxy (Nginx)
- Database for state persistence
- Object storage for reports
- Monitoring and logging
- Load balancing for high availability

## Integration Points

### External Services
- Google GenAI API (LLM)
- Future: Real IQVIA, EXIM, Patent APIs
- Future: Real ClinicalTrials.gov API
- Future: Real web search APIs

### Internal Components
- Tools → Agents → Master Agent → Workflow → API → UI
- Report Generator ← Workflow State
- File System ← Report Generator

## Extension Points

### Adding New Agents
1. Create tool in `src/tools/`
2. Create agent in `src/agents/`
3. Add agent to workflow in `src/workflows/workflow.py`
4. Update Master Agent routing logic

### Adding New Tools
1. Create tool file in `src/tools/`
2. Use `@tool` decorator
3. Export in `src/tools/__init__.py`
4. Integrate with agent

### Customizing Reports
1. Modify `ReportGenerator` class
2. Update PDF/Excel templates
3. Add new sections/sheets
4. Customize styling

## Monitoring and Observability

### Current State
- Basic error logging
- Test coverage (54 tests)

### Recommended Additions
- Structured logging
- Metrics collection
- Performance monitoring
- Error tracking
- User analytics

