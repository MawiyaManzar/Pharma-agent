"""
Tests for LangGraph workflow and Master Agent.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.workflows import DrugRepurposingWorkflow, MasterAgent, WorkflowState


class TestMasterAgent:
    """Tests for Master Agent"""
    
    @pytest.fixture
    def master_agent(self):
        """Create Master Agent instance with mocked LLM"""
        with patch('src.workflows.master_agent.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = Mock()
            mock_llm_class.return_value = mock_llm
            agent = MasterAgent()
            agent.llm = mock_llm
            return agent
    
    def test_master_agent_initialization(self, master_agent):
        """Test Master Agent initializes correctly"""
        assert master_agent.llm is not None
        assert len(master_agent.worker_agents) == 6
        assert "iqvia" in master_agent.worker_agents
        assert "exim" in master_agent.worker_agents
        assert "patent" in master_agent.worker_agents
        assert "clinical_trials" in master_agent.worker_agents
        assert "internal" in master_agent.worker_agents
        assert "web" in master_agent.worker_agents
    
    def test_determine_agents_to_run(self, master_agent):
        """Test agent selection logic"""
        agents = master_agent.determine_agents_to_run("Analyze Metformin", "Metformin")
        assert isinstance(agents, list)
        assert len(agents) > 0
    
    def test_execute_agent(self, master_agent):
        """Test executing a worker agent"""
        with patch.object(master_agent.worker_agents["iqvia"], 'analyze') as mock_analyze:
            mock_analyze.return_value = {
                "agent_name": "IQVIA Insights Agent",
                "analysis": "Test analysis",
                "key_findings": [],
                "recommendations": []
            }
            
            result = master_agent.execute_agent("iqvia", "Metformin")
            assert result["agent_name"] == "IQVIA Insights Agent"
    
    def test_synthesize_results(self, master_agent):
        """Test result synthesis"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Synthesized analysis"
        master_agent.llm.invoke.return_value = mock_response
        
        results = {
            "iqvia": {
                "agent_name": "IQVIA Insights Agent",
                "analysis": "Market analysis",
                "key_findings": ["Finding 1"],
                "recommendations": ["Rec 1"]
            },
            "exim": {
                "agent_name": "EXIM Trade Agent",
                "analysis": "Trade analysis",
                "key_findings": ["Finding 2"],
                "recommendations": ["Rec 2"]
            }
        }
        
        synthesized = master_agent.synthesize_results(results, "Metformin", "Analyze Metformin")
        assert "synthesis" in synthesized
        assert "key_findings" in synthesized
        assert "recommendations" in synthesized
        assert synthesized["molecule"] == "Metformin"


class TestDrugRepurposingWorkflow:
    """Tests for Drug Repurposing Workflow"""
    
    @pytest.fixture
    def workflow(self):
        """Create workflow instance with mocked components"""
        with patch('src.workflows.workflow.MasterAgent') as mock_master:
            mock_master_instance = Mock()
            mock_master.return_value = mock_master_instance
            mock_master_instance.determine_agents_to_run.return_value = ["iqvia", "exim"]
            mock_master_instance.execute_agent.return_value = {
                "agent_name": "Test Agent",
                "analysis": "Test",
                "key_findings": [],
                "recommendations": []
            }
            mock_master_instance.synthesize_results.return_value = {
                "synthesis": "Test synthesis",
                "key_findings": [],
                "recommendations": []
            }
            
            wf = DrugRepurposingWorkflow()
            wf.master_agent = mock_master_instance
            return wf
    
    def test_workflow_initialization(self, workflow):
        """Test workflow initializes correctly"""
        assert workflow.master_agent is not None
        assert workflow.graph is not None
    
    def test_plan_node(self, workflow):
        """Test planning node"""
        state: WorkflowState = {
            "molecule": "Metformin",
            "user_query": "Analyze Metformin",
            "context": {},
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
            "current_step": "",
            "error": None,
            "messages": [],
        }
        
        result = workflow._plan_node(state)
        assert result["current_step"] == "planning"
        assert len(result["agents_to_run"]) > 0
    
    def test_execute_agent_nodes(self, workflow):
        """Test agent execution nodes"""
        state: WorkflowState = {
            "molecule": "Metformin",
            "user_query": "Analyze Metformin",
            "context": {},
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
            "current_step": "",
            "error": None,
            "messages": [],
        }
        
        # Test IQVIA node
        result = workflow._execute_iqvia_node(state)
        assert result["iqvia_result"] is not None
        assert "iqvia" in result["agents_completed"]
    
    def test_synthesize_node(self, workflow):
        """Test synthesis node"""
        state: WorkflowState = {
            "molecule": "Metformin",
            "user_query": "Analyze Metformin",
            "context": {},
            "agents_to_run": [],
            "agents_completed": [],
            "agents_failed": [],
            "iqvia_result": {"agent_name": "IQVIA", "analysis": "Test"},
            "exim_result": {"agent_name": "EXIM", "analysis": "Test"},
            "patent_result": None,
            "clinical_trials_result": None,
            "internal_result": None,
            "web_result": None,
            "synthesized_result": None,
            "report_data": None,
            "current_step": "",
            "error": None,
            "messages": [],
        }
        
        result = workflow._synthesize_node(state)
        assert result["synthesized_result"] is not None
        assert result["report_data"] is not None
        assert result["current_step"] == "completed"




