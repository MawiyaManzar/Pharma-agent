"""
State schema for LangGraph workflow.
Defines the state structure for the multi-agent orchestration.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class WorkflowState(TypedDict):
    """
    State schema for the drug repurposing workflow.
    
    This state is passed between nodes in the LangGraph workflow.
    """
    # Input
    molecule: str  # Name of the molecule to analyze
    user_query: str  # Original user query
    context: Optional[Dict[str, Any]]  # Additional context (region, indication, etc.)
    
    # Agent execution tracking
    agents_to_run: List[str]  # List of agent names to execute
    agents_completed: List[str]  # List of completed agent names
    agents_failed: List[str]  # List of failed agent names
    
    # Agent results
    iqvia_result: Optional[Dict[str, Any]]  # IQVIA Insights Agent result
    exim_result: Optional[Dict[str, Any]]  # EXIM Trade Agent result
    patent_result: Optional[Dict[str, Any]]  # Patent Landscape Agent result
    clinical_trials_result: Optional[Dict[str, Any]]  # Clinical Trials Agent result
    internal_result: Optional[Dict[str, Any]]  # Internal Insights Agent result
    web_result: Optional[Dict[str, Any]]  # Web Intelligence Agent result
    
    # Synthesis
    synthesized_result: Optional[Dict[str, Any]]  # Final synthesized result
    report_data: Optional[Dict[str, Any]]  # Data formatted for report generation
    
    # Workflow control
    current_step: str  # Current workflow step
    error: Optional[str]  # Error message if any
    messages: Annotated[List[BaseMessage], add_messages]  # Message history for LLM context




