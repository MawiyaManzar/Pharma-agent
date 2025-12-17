# Architecture Flow: User Input to Report Generation

## Complete End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT (Streamlit Frontend)                                      │
│    - User enters molecule name (e.g., "Metformin")                      │
│    - User submits query (e.g., "Analyze for repurposing opportunities") │
│    - Streamlit sends POST request to FastAPI                            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTP POST /chats
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. FASTAPI BACKEND (src/api/main.py)                                    │
│    - Receives ChatRequest (message, molecule, session_id)               │
│    - Extracts molecule name from request                                │
│    - Initializes DrugRepurposingWorkflow                                │
│    - Calls workflow.run() via asyncio.to_thread()                      │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ workflow.run()
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. LANGGRAPH WORKFLOW (src/workflows/workflow.py)                       │
│                                                                          │
│    Step 3.1: PLAN NODE                                                  │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │ - MasterAgent.determine_agents_to_run()                      │    │
│    │ - Returns list of 6 agents to execute                        │    │
│    │ - Updates state: agents_to_run = [all 6 agents]             │    │
│    └──────────────────────────────────────────────────────────────┘    │
│                                │                                         │
│                                ▼                                         │
│    Step 3.2: SEQUENTIAL AGENT EXECUTION (BOTTLENECK #1)                │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │ execute_iqvia → execute_exim → execute_patent →               │    │
│    │ execute_clinical_trials → execute_internal → execute_web     │    │
│    │                                                               │    │
│    │ Each agent execution:                                        │    │
│    │   1. MasterAgent.execute_agent(agent_name, molecule)         │    │
│    │   2. Worker Agent.analyze(molecule)                           │    │
│    │      a. Calls tool to get raw_data (FAST - mock data)         │    │
│    │      b. Builds analysis prompt                                │    │
│    │      c. LLM call: self.agent.invoke(messages) [SLOW]         │    │
│    │      d. Formats insights (raw_data + analysis)               │    │
│    │   3. Updates workflow state with result                       │    │
│    └──────────────────────────────────────────────────────────────┘    │
│                                │                                         │
│                                ▼                                         │
│    Step 3.3: SYNTHESIZE NODE (BOTTLENECK #2)                             │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │ - Collects all agent results                                 │    │
│    │ - MasterAgent.synthesize_results()                            │    │
│    │   a. Builds synthesis prompt with all agent analyses          │    │
│    │   b. LLM call #1: Full synthesis [SLOW]                       │    │
│    │   c. Builds summary prompt                                    │    │
│    │   d. LLM call #2: Executive summary [SLOW]                   │    │
│    │ - Prepares report_data structure                              │    │
│    └──────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ final_state with report_data
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. REPORT GENERATION (src/reports/report_generator.py)                  │
│    ┌──────────────────────────────────────────────────────────────┐    │
│    │ ReportGenerator.generate_reports(report_data)                │    │
│    │                                                               │    │
│    │ Step 4.1: PDF Generation (BOTTLENECK #3)                      │    │
│    │ - Creates ReportLab document                                 │    │
│    │ - Builds title page, sections, tables                        │    │
│    │ - Renders synthesis text, findings, recommendations            │    │
│    │ - Saves to outputs/ directory                                 │    │
│    │                                                               │    │
│    │ Step 4.2: Excel Generation                                    │    │
│    │ - Creates openpyxl workbook                                  │    │
│    │ - Adds multiple sheets (Summary, Findings, etc.)             │    │
│    │ - Styles cells, sets column widths                           │    │
│    │ - Saves to outputs/ directory                                 │    │
│    └──────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ report_paths
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. RESPONSE (FastAPI → Streamlit)                                       │
│    - Returns ChatResponse with:                                         │
│      - synthesis text                                                  │
│      - key_findings                                                    │
│      - recommendations                                                  │
│      - report_paths (PDF and Excel)                                    │
│      - workflow_state                                                  │
│    - Streamlit displays results and download buttons                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Current Timing Breakdown (Estimated)

Based on the architecture analysis:

| Stage | Component | Estimated Time | Notes |
|-------|-----------|----------------|-------|
| **1. User Input** | Streamlit UI | < 1s | Negligible |
| **2. FastAPI Handler** | Request processing | < 1s | Fast |
| **3.1 Plan Node** | Agent determination | < 1s | Simple logic |
| **3.2 Agent Execution** | **6 Sequential Agents** | **~180-200s** | **MAJOR BOTTLENECK** |
|       | - IQVIA Agent | ~30s | Tool call + LLM call |
|       | - EXIM Agent | ~30s | Tool call + LLM call |
|       | - Patent Agent | ~30s | Tool call + LLM call |
|       | - Clinical Trials Agent | ~30s | Tool call + LLM call |
|       | - Internal Agent | ~30s | Tool call + LLM call |
|       | - Web Agent | ~30s | Tool call + LLM call |
| **3.3 Synthesis** | **MasterAgent** | **~30-40s** | **BOTTLENECK** |
|       | - Full synthesis LLM call | ~20s | Large prompt |
|       | - Summary LLM call | ~10-20s | Summary generation |
| **4. Report Generation** | **PDF + Excel** | **~10-20s** | **BOTTLENECK** |
|       | - PDF generation | ~8-12s | ReportLab rendering |
|       | - Excel generation | ~2-8s | openpyxl operations |
| **5. Response** | FastAPI → Streamlit | < 1s | Fast |
| **TOTAL** | **End-to-End** | **~230-260 seconds** | **~4 minutes** |

## Identified Bottlenecks

### 🔴 Critical Bottlenecks

1. **Sequential Agent Execution (~180-200s)**
   - **Problem**: 6 agents run one after another, each making an LLM call
   - **Impact**: ~30s per agent × 6 agents = ~180s minimum
   - **Root Cause**: LangGraph workflow uses sequential edges (lines 81-87 in workflow.py)

2. **MasterAgent Synthesis (~30-40s)**
   - **Problem**: Two sequential LLM calls (full synthesis + summary)
   - **Impact**: ~20s + ~10-20s = ~30-40s
   - **Root Cause**: Two separate LLM invocations in synthesize_results()

3. **Synchronous Report Generation (~10-20s)**
   - **Problem**: PDF and Excel generation happens synchronously before response
   - **Impact**: User waits for reports even if they only want the synthesis
   - **Root Cause**: Report generation in main request path (line 159 in main.py)

### 🟡 Moderate Bottlenecks

4. **LLM Call Latency**
   - Each LLM call takes ~20-30s (network + processing)
   - Total: 6 agent calls + 2 synthesis calls = 8 LLM calls
   - Could be reduced with faster models or caching

5. **Tool Data Fetching**
   - Each agent calls its tool (though mock data is fast)
   - Could be parallelized if tools were async

## Optimization Opportunities

### 🚀 High-Impact Optimizations

#### 1. **Parallelize Worker Agents** (Potential: 5-6× speedup)
   - **Current**: Sequential execution (~180s)
   - **Optimized**: Parallel execution (~30s for slowest agent)
   - **Implementation**: Use LangGraph's parallel node execution or asyncio.gather()
   - **Complexity**: Medium-High
   - **Risk**: Low (agents are independent)

#### 2. **Combine MasterAgent LLM Calls** (Potential: 1.5-2× speedup)
   - **Current**: 2 separate LLM calls (~30-40s)
   - **Optimized**: Single LLM call with structured output (~20s)
   - **Implementation**: Request both full synthesis and summary in one prompt
   - **Complexity**: Low-Medium
   - **Risk**: Low

#### 3. **Async Report Generation** (Potential: Immediate response)
   - **Current**: Synchronous report generation (~10-20s)
   - **Optimized**: Return synthesis immediately, generate reports in background
   - **Implementation**: Use FastAPI BackgroundTasks or Celery
   - **Complexity**: Low-Medium
   - **Risk**: Low (UI already supports async via /chats/start endpoint)

#### 4. **Remove Unnecessary LLM Calls** (Potential: 6-8× speedup)
   - **Current**: Each worker agent makes an LLM call
   - **Optimized**: Use deterministic analysis from structured data
   - **Implementation**: Build analysis from key_findings + recommendations
   - **Complexity**: Medium
   - **Risk**: Medium (may reduce narrative quality)

### 🟢 Medium-Impact Optimizations

#### 5. **Caching** (Potential: Instant for repeated queries)
   - Cache agent results by (molecule, query) tuple
   - Cache synthesis results
   - **Complexity**: Low
   - **Risk**: Low

#### 6. **Streaming Responses**
   - Stream agent results as they complete
   - Update UI progressively
   - **Complexity**: Medium
   - **Risk**: Low

#### 7. **Report Generation Optimization**
   - Use faster PDF library (e.g., WeasyPrint)
   - Optimize Excel generation (reduce styling operations)
   - **Complexity**: Medium
   - **Risk**: Low

## Recommended Optimization Strategy

### Phase 1: Quick Wins (1-2 hours)
1. ✅ **Async Report Generation** - Move to background task
2. ✅ **Combine MasterAgent Calls** - Single LLM call for synthesis

**Expected Result**: ~230s → ~200s (13% improvement)

### Phase 2: Major Optimization (4-6 hours)
3. ✅ **Parallelize Worker Agents** - Execute all 6 agents concurrently

**Expected Result**: ~200s → ~50-60s (70-75% improvement)

### Phase 3: Advanced Optimization (2-4 hours)
4. ✅ **Remove Worker Agent LLM Calls** - Use deterministic analysis
5. ✅ **Add Caching** - Cache repeated queries

**Expected Result**: ~50-60s → ~10-20s (90% improvement)

## Implementation Priority

| Priority | Optimization | Impact | Effort | Risk |
|----------|--------------|--------|--------|------|
| **P0** | Parallelize Worker Agents | 🔴 High | Medium | Low |
| **P1** | Async Report Generation | 🟡 Medium | Low | Low |
| **P2** | Combine MasterAgent Calls | 🟡 Medium | Low | Low |
| **P3** | Remove Worker LLM Calls | 🟢 High | Medium | Medium |
| **P4** | Add Caching | 🟢 Medium | Low | Low |

## Current Architecture Files

- **Frontend**: `src/ui/app.py` - Streamlit UI
- **Backend**: `src/api/main.py` - FastAPI endpoints
- **Workflow**: `src/workflows/workflow.py` - LangGraph orchestration
- **Master Agent**: `src/workflows/master_agent.py` - Synthesis logic
- **Worker Agents**: `src/agents/*.py` - 6 specialized agents
- **Tools**: `src/tools/*.py` - Mock data sources
- **Reports**: `src/reports/report_generator.py` - PDF/Excel generation

## Next Steps

1. **Profile the system** - Add timing logs to measure actual bottlenecks
2. **Implement Phase 1 optimizations** - Quick wins
3. **Implement Phase 2** - Parallel agent execution
4. **Measure and iterate** - Validate improvements

