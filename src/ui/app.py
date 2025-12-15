"""
Streamlit frontend application for Pharma Agentic AI.
Connects to FastAPI backend for processing queries.
"""

import streamlit as st
import requests
import os
from typing import Optional
import time

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Pharma Agentic AI - Drug Repurposing Intelligence",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Pharma Agentic AI")
st.title("Drug Repurposing Intelligence Platform")

# Initialize session state
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_report_paths" not in st.session_state:
    st.session_state.last_report_paths = None
if "workflow_status" not in st.session_state:
    st.session_state.workflow_status = None


def call_api(message: str, molecule: Optional[str] = None) -> dict:
    """
    Call the FastAPI /chats endpoint
    
    Args:
        message: User query message
        molecule: Optional molecule name
        
    Returns:
        API response as dictionary
    """
    try:
        response = requests.post(
            f"{API_URL}/chats",
            json={
                "message": message,
                "molecule": molecule,
                "session_id": st.session_state.session_id
            },
            timeout=600  # 10 minute timeout for long-running queries
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {
            "response": "Error: Request timed out. The analysis is taking longer than expected.",
            "status": "timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "response": f"Error: Could not connect to backend API - {str(e)}",
            "status": "error"
        }


# Sidebar for molecule input
with st.sidebar:
    st.header("🔬 Molecule Information")
    molecule_name = st.text_input(
        "Enter molecule name",
        placeholder="e.g., Metformin, Aspirin",
        help="Enter the molecule you want to analyze for repurposing opportunities"
    )
    
    st.divider()
    st.info("💡 **Tip**: Enter a molecule name and ask questions about repurposing opportunities, market potential, or clinical trials.")

# Main chat interface
st.header("Chat with Pharma AI")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask about drug repurposing opportunities..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Show thinking indicator with progress
    with st.chat_message("assistant"):
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Show workflow steps
        status_text.text("🔄 Initializing workflow...")
        progress_bar.progress(10)
        
        # Call API
        api_response = call_api(prompt, molecule_name if molecule_name else None)
        
        # Update progress
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        time.sleep(0.5)  # Brief pause to show completion
        progress_bar.empty()
        status_text.empty()
        
        # Display response
        response_text = api_response.get("response", "No response received")
        status = api_response.get("status", "unknown")
        
        if status == "completed":
            st.success("✅ Analysis completed successfully!")
            st.write(response_text)
            
            # Show workflow status
            workflow_state = api_response.get("workflow_state")
            if workflow_state:
                with st.expander("📊 Workflow Status"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Agents Completed", len(workflow_state.get("agents_completed", [])))
                    with col2:
                        st.metric("Agents Failed", len(workflow_state.get("agents_failed", [])))
                    
                    if workflow_state.get("agents_completed"):
                        st.write("**Completed Agents:**")
                        for agent in workflow_state["agents_completed"]:
                            st.write(f"  ✓ {agent.replace('_', ' ').title()}")
            
            # Show key findings and recommendations
            data = api_response.get("data", {})
            if data:
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("🔍 Key Findings"):
                        findings = data.get("key_findings", [])
                        if findings:
                            for finding in findings[:10]:  # Show top 10
                                st.write(f"• {finding}")
                        else:
                            st.info("No key findings available.")
                
                with col2:
                    with st.expander("💡 Recommendations"):
                        recommendations = data.get("recommendations", [])
                        if recommendations:
                            for rec in recommendations[:10]:  # Show top 10
                                st.write(f"• {rec}")
                        else:
                            st.info("No recommendations available.")
            
            # Report download section
            report_paths = api_response.get("report_paths")
            if report_paths:
                st.session_state.last_report_paths = report_paths
                st.divider()
                st.subheader("📥 Download Reports")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    pdf_filename = report_paths.get("pdf", "").split("/")[-1]
                    if pdf_filename:
                        pdf_url = f"{API_URL}/reports/pdf/{pdf_filename}"
                        # Fetch PDF content for download
                        try:
                            pdf_response = requests.get(pdf_url, timeout=30)
                            if pdf_response.status_code == 200:
                                st.download_button(
                                    label="📄 Download PDF Report",
                                    data=pdf_response.content,
                                    file_name=pdf_filename,
                                    mime="application/pdf",
                                    key="pdf_download"
                                )
                            else:
                                st.error(f"Could not download PDF: {pdf_response.status_code}")
                        except Exception as e:
                            st.error(f"Error downloading PDF: {str(e)}")
                            st.info(f"Direct link: [{pdf_filename}]({pdf_url})")
                
                with col2:
                    excel_filename = report_paths.get("excel", "").split("/")[-1]
                    if excel_filename:
                        excel_url = f"{API_URL}/reports/excel/{excel_filename}"
                        # Fetch Excel content for download
                        try:
                            excel_response = requests.get(excel_url, timeout=30)
                            if excel_response.status_code == 200:
                                st.download_button(
                                    label="📊 Download Excel Report",
                                    data=excel_response.content,
                                    file_name=excel_filename,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="excel_download"
                                )
                            else:
                                st.error(f"Could not download Excel: {excel_response.status_code}")
                        except Exception as e:
                            st.error(f"Error downloading Excel: {str(e)}")
                            st.info(f"Direct link: [{excel_filename}]({excel_url})")
            
            # Show additional data if available
            if api_response.get("data"):
                with st.expander("🔬 View Full Analysis Data"):
                    st.json(api_response["data"])
        
        elif status == "error" or status == "timeout":
            st.error("❌ " + response_text)
            st.info("Please try again or contact support if the issue persists.")
        else:
            st.warning("⚠️ " + response_text)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Note: We don't clear molecule_name here as it's a session state variable
    # The user can manually clear it if needed

# Footer with additional info
st.divider()

# Show last report info if available
if st.session_state.last_report_paths:
    with st.expander("📋 Last Generated Reports"):
        st.write(f"**PDF:** `{st.session_state.last_report_paths.get('pdf', 'N/A')}`")
        st.write(f"**Excel:** `{st.session_state.last_report_paths.get('excel', 'N/A')}`")

col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🆔 Session: {st.session_state.session_id[:8]}...")
with col2:
    st.caption(f"🔗 API: {API_URL}")
with col3:
    st.caption("💊 Pharma Agentic AI v0.1.0")


