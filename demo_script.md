# Pharma Agentic AI - Demo Script

## Demo Overview
This demo showcases a complete end-to-end flow of the Drug Repurposing Intelligence Platform, from molecule input to downloadable PDF/Excel reports.

**Target Duration**: 4 minutes

## Pre-Demo Setup

### 1. Start the Backend API
```bash
# Terminal 1
cd /home/mawiya/Desktop/Backup/Pharma-agent
source .venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

### 2. Start the Streamlit Frontend
```bash
# Terminal 2
cd /home/mawiya/Desktop/Backup/Pharma-agent
source .venv/bin/activate
streamlit run src/ui/app.py
```

### 3. Verify Services
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501
- Health check: http://localhost:8000/health

## Demo Flow

### Step 1: Introduction (30 seconds)
**Narrator**: "Today I'll demonstrate our Drug Repurposing Intelligence Platform. This system uses AI agents to analyze pharmaceutical molecules and identify repurposing opportunities across multiple dimensions: market intelligence, trade data, patent landscape, clinical trials, internal insights, and web intelligence."

**Action**: Open Streamlit UI in browser

### Step 2: Molecule Input (30 seconds)
**Narrator**: "Let's analyze Metformin, a well-known diabetes drug, for potential repurposing opportunities."

**Action**:
1. Enter "Metformin" in the molecule input field
2. Type query: "Analyze Metformin for repurposing opportunities in cardiovascular and oncology indications"

### Step 3: Workflow Execution (2 minutes)
**Narrator**: "The system is now orchestrating six specialized AI agents, each analyzing a different aspect of the molecule."

**Action**: 
- Show progress bar
- Explain what's happening:
  - "IQVIA Insights Agent is analyzing market size and competition"
  - "EXIM Trade Agent is assessing supply chain and trade flows"
  - "Patent Landscape Agent is evaluating FTO and patent risks"
  - "Clinical Trials Agent is identifying active research"
  - "Internal Insights Agent is checking strategic alignment"
  - "Web Intelligence Agent is gathering scientific evidence"

**Wait for completion** (this may take 1-2 minutes with real LLM calls)

### Step 4: Results Display (45 seconds)
**Narrator**: "The Master Agent has synthesized all findings into a comprehensive strategic analysis."

**Action**:
1. Show the synthesized analysis
2. Expand "Key Findings" section - highlight 2-3 findings
3. Expand "Recommendations" section - highlight 2-3 recommendations
4. Show "Workflow Status" - point out all 6 agents completed successfully

### Step 5: Report Download (15 seconds)
**Narrator**: "The system has generated professional PDF and Excel reports with all the analysis."

**Action**:
1. Click "Download PDF Report" button
2. Click "Download Excel Report" button
3. Briefly show the downloaded files

### Step 6: Closing (10 seconds)
**Narrator**: "This demonstrates how our platform accelerates drug repurposing research from months to minutes, providing comprehensive intelligence across market, IP, clinical, and strategic dimensions."

## Test Molecules for Demo

### Primary Demo Molecule
- **Metformin**: Well-known, good for demonstrating all aspects

### Alternative Molecules (if needed)
- **Aspirin**: Common, multiple indications
- **Metformin**: Diabetes drug with repurposing potential
- **Sildenafil**: Viagra, repurposed for pulmonary hypertension

## Demo Tips

1. **Timing**: The workflow execution may take 1-2 minutes. Use this time to explain the architecture.

2. **Error Handling**: If an agent fails, explain that the system is resilient and continues with successful agents.

3. **Reports**: Have the reports open in advance to show if download is slow.

4. **Key Points to Emphasize**:
   - Multi-agent orchestration
   - Comprehensive analysis across 6 domains
   - Strategic synthesis
   - Professional report generation
   - Time savings (months → minutes)

## Troubleshooting

### If Backend Fails to Start
- Check if port 8000 is available
- Verify GOOGLE_API_KEY is set in .env file
- Check virtual environment is activated

### If Frontend Fails to Connect
- Verify backend is running
- Check API_URL in environment
- Check CORS settings

### If Workflow Takes Too Long
- Explain that real LLM calls take time
- Show progress indicators
- Use this time to explain the system architecture

### If Reports Don't Generate
- Check outputs/ directory exists
- Verify reportlab and openpyxl are installed
- Check file permissions

## Post-Demo

### Questions to Prepare For
1. "How accurate is the analysis?"
   - Response: "The system uses Google's Gemini model and realistic mock data. In production, it would connect to real APIs."

2. "Can it handle multiple molecules?"
   - Response: "Yes, each query is independent. You can analyze multiple molecules sequentially."

3. "How does it compare to manual research?"
   - Response: "Manual research takes 2-3 months. This system provides comprehensive analysis in minutes, though it's designed to augment, not replace, human expertise."

4. "What about data privacy?"
   - Response: "All processing happens locally/in your infrastructure. No data is sent to external services except the LLM API."

## Demo Checklist

- [ ] Backend API running on port 8000
- [ ] Streamlit UI running on port 8501
- [ ] GOOGLE_API_KEY configured
- [ ] Test molecule selected (Metformin)
- [ ] Sample reports generated in outputs/
- [ ] Browser ready with UI open
- [ ] Demo script reviewed
- [ ] Troubleshooting guide reviewed



