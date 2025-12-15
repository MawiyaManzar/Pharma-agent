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
import asyncio
from pathlib import Path

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

