# Integration Testing Guide

## Overview
This document describes how to run end-to-end integration tests for the Pharma Agentic AI system.

## Running Integration Tests

### Prerequisites
1. Virtual environment activated
2. All dependencies installed
3. GOOGLE_API_KEY set in .env file (for full tests)
4. outputs/ directory exists

### Run All Integration Tests
```bash
pytest tests/test_integration.py -v
```

### Run Specific Test Classes
```bash
# Test end-to-end integration
pytest tests/test_integration.py::TestEndToEndIntegration -v

# Test system components
pytest tests/test_integration.py::TestSystemComponents -v
```

### Run with Coverage
```bash
pytest tests/test_integration.py --cov=src --cov-report=html
```

## Test Categories

### 1. API Integration Tests
- Health check endpoint
- Root endpoint
- /chats endpoint with workflow integration
- Report download endpoints
- Error handling

### 2. Workflow Integration Tests
- Workflow execution flow
- Agent orchestration
- State management
- Result synthesis

### 3. Report Generation Tests
- PDF generation from workflow output
- Excel generation from workflow output
- File existence and format validation

### 4. End-to-End User Journey
- Complete flow from API request to report download
- Data flow validation
- Error recovery

## Manual Testing Checklist

### Backend API Testing
- [ ] Health endpoint returns 200
- [ ] Root endpoint returns API info
- [ ] /chats endpoint accepts POST requests
- [ ] /chats endpoint executes workflow
- [ ] /chats endpoint generates reports
- [ ] /chats endpoint returns proper response structure
- [ ] Report download endpoints work
- [ ] Error handling works correctly

### Frontend UI Testing
- [ ] Streamlit app starts without errors
- [ ] Molecule input works
- [ ] Query submission works
- [ ] Progress indicators display
- [ ] Results display correctly
- [ ] Key findings expandable section works
- [ ] Recommendations expandable section works
- [ ] Workflow status displays correctly
- [ ] PDF download button works
- [ ] Excel download button works
- [ ] Error messages display correctly

### Workflow Testing
- [ ] All 6 agents execute
- [ ] Agent results are collected
- [ ] Synthesis happens correctly
- [ ] Report data is prepared
- [ ] State transitions work
- [ ] Error handling in workflow

### Report Generation Testing
- [ ] PDF generates successfully
- [ ] Excel generates successfully
- [ ] PDF contains all sections
- [ ] Excel contains all sheets
- [ ] Files are saved to outputs/
- [ ] Filenames are correct

## Performance Testing

### Expected Timings
- Workflow execution: 1-3 minutes (with real LLM calls)
- Report generation: 5-10 seconds
- Total end-to-end: 2-4 minutes

### Load Testing
- Test with multiple concurrent requests
- Test with different molecule names
- Test error recovery

## Known Issues and Limitations

1. **LLM API Calls**: Real LLM calls take time. Tests use mocks for speed.
2. **File Cleanup**: Test files may remain in outputs/ directory
3. **Concurrent Requests**: System not optimized for high concurrency yet

## Continuous Integration

### GitHub Actions (if applicable)
```yaml
# Example CI configuration
- name: Run Integration Tests
  run: |
    pytest tests/test_integration.py -v
```

## Test Data

### Sample Molecules for Testing
- Metformin
- Aspirin
- Sildenafil
- Ibuprofen

### Sample Queries
- "Analyze [molecule] for repurposing opportunities"
- "What are the market opportunities for [molecule]?"
- "Assess [molecule] for new indications"

## Debugging Failed Tests

1. Check logs for error messages
2. Verify environment variables
3. Check file permissions
4. Verify dependencies are installed
5. Check network connectivity (for LLM API)

## Next Steps

After integration tests pass:
1. Run manual demo
2. Prepare demo script
3. Document any issues found
4. Update system based on test results



