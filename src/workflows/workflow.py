"""
LangGraph workflow for orchestrating multi-agent drug repurposing analysis.
"""

from typing import Dict, Any, Optional, Callable, Tuple
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .state import WorkflowState
from .master_agent import MasterAgent


class DrugRepurposingWorkflow:
    """
    LangGraph workflow for orchestrating drug repurposing analysis.
    
    This workflow coordinates the execution of multiple specialized agents
    to analyze pharmaceutical molecules for repurposing opportunities.
    
    Workflow Steps:
    1. Plan: Determine which agents to execute
    2. Execute Agents: Run worker agents in parallel (concurrent execution)
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
        - Execution: Single node that executes all 6 agents in parallel
        - Synthesis: combine results
        - Exit: END node
        
        Returns:
            Compiled LangGraph StateGraph with memory checkpoint
        """
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute_all_agents", self._execute_all_agents_parallel)
        workflow.add_node("synthesize", self._synthesize_node)
        
        # Set entry point
        workflow.set_entry_point("plan")
        
        # Add edges: plan → execute_all_agents (parallel) → synthesize → end
        workflow.add_edge("plan", "execute_all_agents")
        workflow.add_edge("execute_all_agents", "synthesize")
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
    
    def _execute_single_agent(self, agent_name: str, molecule: str, context: Dict[str, Any], state_lock: threading.Lock) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """
        Execute a single agent and return result.
        
        Args:
            agent_name: Name of the agent to execute
            molecule: Molecule name
            context: Context dictionary
            state_lock: Lock for thread-safe state updates
            
        Returns:
            Tuple of (agent_name, result_dict, error_message)
        """
        try:
            result = self.master_agent.execute_agent(agent_name, molecule, context)
            return (agent_name, result, None)
        except Exception as e:
            error_msg = str(e)
            return (agent_name, {"error": error_msg, "status": "failed"}, error_msg)
    
    def _execute_all_agents_parallel(self, state: WorkflowState) -> WorkflowState:
        """
        Execute all worker agents in parallel using ThreadPoolExecutor.
        
        This replaces the sequential execution with concurrent execution,
        significantly reducing total execution time from ~180s to ~30s.
        """
        state["current_step"] = "executing_agents_parallel"
        messages = state.get("messages") or []
        messages.append("Running all worker agents in parallel...")
        
        molecule = state["molecule"]
        context = state.get("context") or {}
        
        # Define all agents to execute
        agents_to_run = [
            "iqvia",
            "exim", 
            "patent",
            "clinical_trials",
            "internal",
            "web"
        ]
        
        # Thread-safe lock for state updates
        state_lock = threading.Lock()
        
        # Execute all agents concurrently using ThreadPoolExecutor
        results = {}
        completed_agents = []
        failed_agents = []
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(self._execute_single_agent, agent_name, molecule, context, state_lock): agent_name
                for agent_name in agents_to_run
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    agent_name_result, result_dict, error_msg = future.result()
                    
                    # Update state with result
                    results[agent_name_result] = result_dict
                    
                    if error_msg:
                        failed_agents.append(agent_name_result)
                        with state_lock:
                            messages.append(f"{agent_name_result.replace('_', ' ').title()} Agent failed: {error_msg}")
                    else:
                        completed_agents.append(agent_name_result)
                        with state_lock:
                            messages.append(f"{agent_name_result.replace('_', ' ').title()} Agent completed successfully.")
                            
                except Exception as e:
                    # Handle unexpected errors
                    results[agent_name] = {"error": str(e), "status": "failed"}
                    failed_agents.append(agent_name)
                    with state_lock:
                        messages.append(f"{agent_name.replace('_', ' ').title()} Agent failed with unexpected error: {str(e)}")
        
        # Update state with all results
        state["iqvia_result"] = results.get("iqvia")
        state["exim_result"] = results.get("exim")
        state["patent_result"] = results.get("patent")
        state["clinical_trials_result"] = results.get("clinical_trials")
        state["internal_result"] = results.get("internal")
        state["web_result"] = results.get("web")
        
        # Update agent tracking
        state["agents_completed"] = completed_agents
        state["agents_failed"] = failed_agents
        
        state["messages"] = messages
        state["current_step"] = "agents_completed"
        
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

