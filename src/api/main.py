"""
FastAPI backend application for Pharma Agentic AI.
Provides API endpoints for the Streamlit frontend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4
import asyncio

import sys
import traceback

# Try to import dependencies with better error handling
try:
    from src.workflows import DrugRepurposingWorkflow
    from src.reports import ReportGenerator
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}", file=sys.stderr)
    print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
    print("\nPlease ensure all dependencies are installed:", file=sys.stderr)
    print("  pip install -r requirements.txt", file=sys.stderr)
    raise

load_dotenv()

# In-memory store for background workflow jobs
WORKFLOW_JOBS: Dict[str, Dict[str, Any]] = {}


app = FastAPI(
    title="Pharma Agentic AI API",
    description="API for drug repurposing intelligence platform",
    version="0.1.0"
)

# CORS middleware to allow Streamlit frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    molecule: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    status: str
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    report_paths: Optional[Dict[str, str]] = None
    workflow_state: Optional[Dict[str, Any]] = None


class ChatJobStartResponse(BaseModel):
    """Response model when starting a background job"""
    job_id: str
    status: str


class ChatJobStatusResponse(BaseModel):
    """Response model for job status polling"""
    job_id: str
    status: str
    error: Optional[str] = None
    workflow_state: Optional[Dict[str, Any]] = None
    result: Optional[ChatResponse] = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pharma Agentic AI API",
        "version": "0.1.0",
        "endpoints": {
            "chats": "/chats"
        }
    }


@app.post("/chats", response_model=ChatResponse)
async def chats(request: ChatRequest):
    """
    Main chat endpoint for processing molecule repurposing queries.
    
    This endpoint:
    1. Receives molecule query from Streamlit frontend
    2. Orchestrates the multi-agent workflow using LangGraph
    3. Generates PDF and Excel reports
    4. Returns synthesized results with report paths
    
    Args:
        request: ChatRequest containing message and optional molecule name
        
    Returns:
        ChatResponse with results, status, report paths, and workflow state
    """
    try:
        # Extract molecule from request
        molecule = request.molecule or request.message.split()[0] if request.message else "Unknown"
        
        # If molecule is not explicitly provided, try to extract from message
        if not request.molecule and request.message:
            # Simple extraction - look for molecule name in message
            # In production, this could use NLP to extract molecule names
            words = request.message.split()
            if len(words) > 0:
                # Assume first word or quoted phrase might be molecule
                molecule = words[0].strip('"\'')
        
        # Initialize workflow
        workflow = DrugRepurposingWorkflow()
        
        # Prepare context
        context = {}
        if request.molecule:
            context["molecule"] = request.molecule
        
        # Run workflow (this may take time)
        final_state = await asyncio.to_thread(
            workflow.run,
            molecule=molecule,
            query=request.message,
            context=context
        )
        
        # Extract synthesized result
        synthesized_result = final_state.get("synthesized_result")
        report_data = final_state.get("report_data")
        
        if not synthesized_result:
            raise HTTPException(
                status_code=500,
                detail="Workflow did not produce synthesized results"
            )
        
        # Generate reports
        report_generator = ReportGenerator()
        report_paths = None
        
        if report_data:
            try:
                reports = report_generator.generate_reports(report_data)
                report_paths = {
                    "pdf": reports["pdf"],
                    "excel": reports["excel"],
                    "base_filename": reports["base_filename"]
                }
            except Exception as e:
                # Log error but don't fail the request
                print(f"Report generation error: {str(e)}")
        
        # Prepare response
        synthesis_text = synthesized_result.get("synthesis", "Analysis completed successfully.")
        
        return ChatResponse(
            response=synthesis_text,
            status="completed",
            session_id=request.session_id or "default",
            data={
                "molecule": molecule,
                "synthesis": synthesis_text,
                "key_findings": synthesized_result.get("key_findings", []),
                "recommendations": synthesized_result.get("recommendations", []),
                "summary": synthesized_result.get("summary", {}),
            },
            report_paths=report_paths,
            workflow_state={
                "agents_completed": final_state.get("agents_completed", []),
                "agents_failed": final_state.get("agents_failed", []),
                "current_step": final_state.get("current_step", "unknown"),
                "messages": final_state.get("messages", []),
            }
        )
    
    except ImportError as e:
        # Handle missing dependencies
        error_msg = f"Missing dependency: {str(e)}. Please install requirements: pip install -r requirements.txt"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
    except ValueError as e:
        # Handle missing environment variables (e.g., GOOGLE_API_KEY)
        error_msg = f"Configuration error: {str(e)}. Please check your .env file."
        print(f"ERROR: {error_msg}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )
    except Exception as e:
        # Log full traceback for debugging
        error_detail = f"Error processing request: {str(e)}"
        print(f"ERROR: {error_detail}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


def _run_workflow_job(job_id: str, request_data: Dict[str, Any]) -> None:
    """
    Background task to run the workflow and store progress/results in WORKFLOW_JOBS.
    This allows the frontend to poll for real-time status.
    """
    try:
        WORKFLOW_JOBS[job_id]["status"] = "running"
        WORKFLOW_JOBS[job_id]["error"] = None

        message = request_data.get("message") or ""
        molecule = request_data.get("molecule") or (message.split()[0] if message else "Unknown")

        # Initialize workflow
        workflow = DrugRepurposingWorkflow()

        # Prepare context
        context: Dict[str, Any] = {}
        if request_data.get("molecule"):
            context["molecule"] = request_data["molecule"]

        # Callback to push intermediate state into WORKFLOW_JOBS for live updates
        def on_state_update(state: Dict[str, Any]) -> None:
            WORKFLOW_JOBS[job_id]["workflow_state"] = {
                "agents_completed": state.get("agents_completed", []),
                "agents_failed": state.get("agents_failed", []),
                "current_step": state.get("current_step", "unknown"),
                "messages": state.get("messages", []),
            }

        # Run workflow (synchronously in this background task) with streaming updates
        final_state = workflow.run(
            molecule=molecule,
            query=message,
            context=context,
            on_state_update=on_state_update,
        )

        # Extract synthesized result
        synthesized_result = final_state.get("synthesized_result")
        report_data = final_state.get("report_data")

        if not synthesized_result:
            WORKFLOW_JOBS[job_id]["status"] = "failed"
            WORKFLOW_JOBS[job_id]["error"] = "Workflow did not produce synthesized results"
            WORKFLOW_JOBS[job_id]["workflow_state"] = final_state
            return

        # Generate reports
        report_generator = ReportGenerator()
        report_paths = None

        if report_data:
            try:
                reports = report_generator.generate_reports(report_data)
                report_paths = {
                    "pdf": reports["pdf"],
                    "excel": reports["excel"],
                    "base_filename": reports["base_filename"]
                }
            except Exception as e:
                # Log error but don't fail the job
                print(f"Report generation error (job {job_id}): {str(e)}")

        # Prepare response-like payload
        synthesis_text = synthesized_result.get("synthesis", "Analysis completed successfully.")

        result_payload = ChatResponse(
            response=synthesis_text,
            status="completed",
            session_id=request_data.get("session_id") or "default",
            data={
                "molecule": molecule,
                "synthesis": synthesis_text,
                "key_findings": synthesized_result.get("key_findings", []),
                "recommendations": synthesized_result.get("recommendations", []),
                "summary": synthesized_result.get("summary", {}),
            },
            report_paths=report_paths,
            workflow_state={
                "agents_completed": final_state.get("agents_completed", []),
                "agents_failed": final_state.get("agents_failed", []),
                "current_step": final_state.get("current_step", "unknown"),
                "messages": final_state.get("messages", []),
            }
        )

        WORKFLOW_JOBS[job_id]["status"] = "completed"
        WORKFLOW_JOBS[job_id]["workflow_state"] = result_payload.workflow_state
        WORKFLOW_JOBS[job_id]["result"] = result_payload

    except Exception as e:
        error_detail = f"Error in background job {job_id}: {str(e)}"
        print(f"ERROR: {error_detail}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        WORKFLOW_JOBS[job_id]["status"] = "failed"
        WORKFLOW_JOBS[job_id]["error"] = error_detail


@app.post("/chats/start", response_model=ChatJobStartResponse)
async def chats_start(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Start a chat workflow as a background job.

    Returns immediately with a job_id that the frontend can use to poll status.
    """
    job_id = f"{request.session_id or 'session'}-{uuid4().hex[:8]}"
    WORKFLOW_JOBS[job_id] = {
        "status": "queued",
        "error": None,
        "workflow_state": None,
        "result": None,
    }

    # Run workflow in background
    background_tasks.add_task(_run_workflow_job, job_id, request.dict())

    return ChatJobStartResponse(job_id=job_id, status="started")


@app.get("/chats/status/{job_id}", response_model=ChatJobStatusResponse)
async def chats_status(job_id: str):
    """
    Get the current status and (when ready) result for a background chat job.
    """
    job = WORKFLOW_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = job.get("result")
    # Pydantic will handle conversion of ChatResponse to nested model
    return ChatJobStatusResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        error=job.get("error"),
        workflow_state=job.get("workflow_state"),
        result=result,
    )


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check if critical imports work
        from src.workflows import DrugRepurposingWorkflow
        from src.reports import ReportGenerator
        
        # Check if GOOGLE_API_KEY is set
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            return {
                "status": "unhealthy",
                "error": "GOOGLE_API_KEY not found in environment variables"
            }
        
        return {
            "status": "healthy",
            "dependencies": "ok",
            "api_key_configured": bool(google_api_key)
        }
    except ImportError as e:
        return {
            "status": "unhealthy",
            "error": f"Missing dependency: {str(e)}",
            "fix": "Run: pip install -r requirements.txt"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/reports/{report_type}/{filename}")
async def download_report(report_type: str, filename: str):
    """
    Download generated report files.
    
    Args:
        report_type: Type of report ('pdf' or 'excel')
        filename: Name of the report file
        
    Returns:
        File response with the report
    """
    # Security: Only allow pdf and excel
    if report_type not in ["pdf", "excel"]:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    # Security: Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Construct file path
    report_path = Path("outputs") / filename
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Determine media type
    media_type = "application/pdf" if report_type == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return FileResponse(
        path=str(report_path),
        media_type=media_type,
        filename=filename
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

