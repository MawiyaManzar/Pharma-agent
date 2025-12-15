"""
LangGraph workflow for orchestrating multi-agent drug repurposing analysis.
"""

from typing import Dict, Any, Optional, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import WorkflowState
from .master_agent import MasterAgent


class DrugRepurposingWorkflow:
    """
    LangGraph workflow for orchestrating drug repurposing analysis.
    
    This workflow coordinates the execution of multiple specialized agents
    to analyze pharmaceutical molecules for repurposing opportunities.
    
    Workflow Steps:
    1. Plan: Determine which agents to execute
    2. Execute Agents: Run worker agents sequentially
       - IQVIA Insights Agent
       - EXIM Trade Agent
       - Patent Landscape Agent
       - Clinical Trials Agent
       - Internal Insights Agent
       - Web Intelligence Agent
    3. Synthesize: Combine all agent results into strategic narrative
    4. Complete: Return final state with reports
    
    Example:
        >>> workflow = DrugRepurposingWorkflow()
        >>> result = workflow.run("Metformin", "Analyze for repurposing")
        >>> print(result["synthesized_result"]["synthesis"])
    """
    
    def __init__(self):
        """
        Initialize the workflow with Master Agent.
        
        Creates a new workflow instance with:
        - Master Agent for orchestration
        - LangGraph state machine
        - Memory checkpoint for state persistence
        """
        self.master_agent = MasterAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow graph.
        
        Creates a state graph with the following structure:
        - Entry: plan node
        - Execution: 6 agent execution nodes (sequential)
        - Synthesis: combine results
        - Exit: END node
        
        Returns:
            Compiled LangGraph StateGraph with memory checkpoint
        """
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute_iqvia", self._execute_iqvia_node)
        workflow.add_node("execute_exim", self._execute_exim_node)
        workflow.add_node("execute_patent", self._execute_patent_node)
        workflow.add_node("execute_clinical_trials", self._execute_clinical_trials_node)
        workflow.add_node("execute_internal", self._execute_internal_node)
        workflow.add_node("execute_web", self._execute_web_node)
        workflow.add_node("synthesize", self._synthesize_node)
        
        # Set entry point
        workflow.set_entry_point("plan")
        
        # Add edges from plan to all agent executions (sequential for now)
        # Note: True parallel execution would require async or threading
        workflow.add_edge("plan", "execute_iqvia")
        workflow.add_edge("execute_iqvia", "execute_exim")
        workflow.add_edge("execute_exim", "execute_patent")
        workflow.add_edge("execute_patent", "execute_clinical_trials")
        workflow.add_edge("execute_clinical_trials", "execute_internal")
        workflow.add_edge("execute_internal", "execute_web")
        workflow.add_edge("execute_web", "synthesize")
        
        # Synthesize to end
        workflow.add_edge("synthesize", END)
        
        # Compile with memory for state persistence
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _plan_node(self, state: WorkflowState) -> WorkflowState:
        """Plan the analysis - determine which agents to run."""
        state["current_step"] = "planning"
        # Initialize or update execution log
        messages = state.get("messages") or []
        messages.append("Planning workflow and determining which agents to run...")
        state["messages"] = messages
        state["agents_to_run"] = self.master_agent.determine_agents_to_run(
            state["user_query"],
            state["molecule"]
        )
        state["agents_completed"] = []
        state["agents_failed"] = []
        return state
    
    def _execute_iqvia_node(self, state: WorkflowState) -> WorkflowState:
        """Execute IQVIA Insights Agent."""
        state["current_step"] = "execute_iqvia"
        messages = state.get("messages") or []
        messages.append("Running IQVIA Insights Agent...")
        try:
            result = self.master_agent.execute_agent("iqvia", state["molecule"], state.get("context"))
            state["iqvia_result"] = result
            state["agents_completed"].append("iqvia")
        except Exception as e:
            state["iqvia_result"] = {"error": str(e), "status": "failed"}
            state["agents_failed"].append("iqvia")
            messages.append(f"IQVIA Insights Agent failed: {str(e)}")
        else:
            messages.append("IQVIA Insights Agent completed successfully.")
        state["messages"] = messages
        return state
    
    def _execute_exim_node(self, state: WorkflowState) -> WorkflowState:
        """Execute EXIM Trade Agent."""
        state["current_step"] = "execute_exim"
        messages = state.get("messages") or []
        messages.append("Running EXIM Trade Agent...")
        try:
            result = self.master_agent.execute_agent("exim", state["molecule"], state.get("context"))
            state["exim_result"] = result
            state["agents_completed"].append("exim")
        except Exception as e:
            state["exim_result"] = {"error": str(e), "status": "failed"}
            state["agents_failed"].append("exim")
            messages.append(f"EXIM Trade Agent failed: {str(e)}")
        else:
            messages.append("EXIM Trade Agent completed successfully.")
        state["messages"] = messages
        return state
    
    def _execute_patent_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Patent Landscape Agent."""
        state["current_step"] = "execute_patent"
        messages = state.get("messages") or []
        messages.append("Running Patent Landscape Agent...")
        try:
            result = self.master_agent.execute_agent("patent", state["molecule"], state.get("context"))
            state["patent_result"] = result
            state["agents_completed"].append("patent")
        except Exception as e:
            state["patent_result"] = {"error": str(e), "status": "failed"}
            state["agents_failed"].append("patent")
            messages.append(f"Patent Landscape Agent failed: {str(e)}")
        else:
            messages.append("Patent Landscape Agent completed successfully.")
        state["messages"] = messages
        return state
    
    def _execute_clinical_trials_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Clinical Trials Agent."""
        state["current_step"] = "execute_clinical_trials"
        messages = state.get("messages") or []
        messages.append("Running Clinical Trials Agent...")
        try:
            result = self.master_agent.execute_agent("clinical_trials", state["molecule"], state.get("context"))
            state["clinical_trials_result"] = result
            state["agents_completed"].append("clinical_trials")
        except Exception as e:
            state["clinical_trials_result"] = {"error": str(e), "status": "failed"}
            state["agents_failed"].append("clinical_trials")
            messages.append(f"Clinical Trials Agent failed: {str(e)}")
        else:
            messages.append("Clinical Trials Agent completed successfully.")
        state["messages"] = messages
        return state
    
    def _execute_internal_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Internal Insights Agent."""
        state["current_step"] = "execute_internal"
        messages = state.get("messages") or []
        messages.append("Running Internal Insights Agent...")
        try:
            result = self.master_agent.execute_agent("internal", state["molecule"], state.get("context"))
            state["internal_result"] = result
            state["agents_completed"].append("internal")
        except Exception as e:
            state["internal_result"] = {"error": str(e), "status": "failed"}
            state["agents_failed"].append("internal")
            messages.append(f"Internal Insights Agent failed: {str(e)}")
        else:
            messages.append("Internal Insights Agent completed successfully.")
        state["messages"] = messages
        return state
    
    def _execute_web_node(self, state: WorkflowState) -> WorkflowState:
        """Execute Web Intelligence Agent."""
        state["current_step"] = "execute_web"
        messages = state.get("messages") or []
        messages.append("Running Web Intelligence Agent...")
        try:
            result = self.master_agent.execute_agent("web", state["molecule"], state.get("context"))
            state["web_result"] = result
            state["agents_completed"].append("web")
        except Exception as e:
            state["web_result"] = {"error": str(e), "status": "failed"}
            state["agents_failed"].append("web")
            messages.append(f"Web Intelligence Agent failed: {str(e)}")
        else:
            messages.append("Web Intelligence Agent completed successfully.")
        state["messages"] = messages
        return state
    
    def _synthesize_node(self, state: WorkflowState) -> WorkflowState:
        """Synthesize all agent results."""
        state["current_step"] = "synthesizing"
        messages = state.get("messages") or []
        messages.append("Synthesizing results from all agents...")
        
        # Collect all results
        results = {
            "iqvia": state.get("iqvia_result"),
            "exim": state.get("exim_result"),
            "patent": state.get("patent_result"),
            "clinical_trials": state.get("clinical_trials_result"),
            "internal": state.get("internal_result"),
            "web": state.get("web_result"),
        }
        
        # Filter out None results
        results = {k: v for k, v in results.items() if v is not None}
        
        # Synthesize
        synthesized = self.master_agent.synthesize_results(
            results,
            state["molecule"],
            state["user_query"]
        )
        
        state["synthesized_result"] = synthesized
        state["report_data"] = self._prepare_report_data(state, results)
        state["current_step"] = "completed"
        messages.append("Workflow completed. Synthesis and report data prepared.")
        state["messages"] = messages
        
        return state
    
    def _prepare_report_data(self, state: WorkflowState, results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data structure for report generation."""
        return {
            "molecule": state["molecule"],
            "query": state["user_query"],
            "synthesis": state.get("synthesized_result", {}).get("synthesis", ""),
            "agent_results": results,
            "key_findings": state.get("synthesized_result", {}).get("key_findings", []),
            "recommendations": state.get("synthesized_result", {}).get("recommendations", []),
            "summary": state.get("synthesized_result", {}).get("summary", {}),
        }
    
    def run(
        self,
        molecule: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        on_state_update: Optional[Callable[[WorkflowState], None]] = None,
    ) -> Dict[str, Any]:
        """
        Run the complete workflow for a molecule analysis.
        
        This method executes the full workflow:
        1. Plans agent execution
        2. Runs all worker agents
        3. Synthesizes results
        4. Prepares report data
        
        Args:
            molecule: Name of the pharmaceutical molecule/drug to analyze
            query: User's query/question about the molecule
            context: Optional context dictionary with additional parameters:
                - region: Geographic region filter (for IQVIA agent)
                - therapy_area: Therapy area filter (for Patent agent)
                - mechanism: Mechanism of action (for Clinical Trials agent)
                - target_indication: Target indication (for Web agent)
                - document_filter: Document type filter (for Internal agent)
        
        Returns:
            Dictionary containing the final workflow state with:
                - molecule: Analyzed molecule name
                - user_query: Original user query
                - synthesized_result: Master Agent's synthesis
                - report_data: Data formatted for report generation
                - agents_completed: List of successfully completed agents
                - agents_failed: List of failed agents
                - current_step: Current workflow step ("completed" on success)
                - Individual agent results (iqvia_result, exim_result, etc.)
        
        Example:
            >>> workflow = DrugRepurposingWorkflow()
            >>> result = workflow.run(
            ...     molecule="Metformin",
            ...     query="Analyze for cardiovascular repurposing",
            ...     context={"region": "US", "therapy_area": "Cardiovascular"}
            ... )
            >>> print(result["synthesized_result"]["synthesis"])
        """
        # Initialize state
        initial_state: WorkflowState = {
            "molecule": molecule,
            "user_query": query,
            "context": context or {},
            "agents_to_run": [],
            "agents_completed": [],
            "agents_failed": [],
            "iqvia_result": None,
            "exim_result": None,
            "patent_result": None,
            "clinical_trials_result": None,
            "internal_result": None,
            "web_result": None,
            "synthesized_result": None,
            "report_data": None,
            "current_step": "initialized",
            "error": None,
            "messages": [],
        }
        
        # Run workflow with streaming so callers can observe intermediate state.
        # NOTE: graph.stream() yields dictionaries of {node_name: state}.
        config = {"configurable": {"thread_id": "1"}}
        final_state: Optional[WorkflowState] = None
        
        for update in self.graph.stream(initial_state, config):
            # Each update is a dict: { "node_name": WorkflowState }
            for _node_name, state in update.items():
                final_state = state
                if on_state_update is not None:
                    on_state_update(state)
        
        return final_state or initial_state

