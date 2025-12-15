"""
Tests for all worker agents.
"""

import pytest
from unittest.mock import Mock, patch
from src.agents import (
    IQVIAInsightsAgent,
    EXIMTradeAgent,
    PatentLandscapeAgent,
    ClinicalTrialsAgent,
    InternalInsightsAgent,
    WebIntelligenceAgent,
    ALL_WORKER_AGENTS,
)


class TestIQVIAInsightsAgent:
    """Tests for IQVIA Insights Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return IQVIAInsightsAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "IQVIA Insights Agent"
        assert agent.role == "Market Intelligence Analyst"
        assert len(agent.tools) == 1
    
    def test_agent_analyze_structure(self, agent):
        """Test analyze method returns correct structure"""
        with patch.object(agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.content = "Test analysis of market data"
            mock_agent.invoke.return_value = mock_response
            
            result = agent.analyze("Metformin")
            
            assert isinstance(result, dict)
            assert "agent_name" in result
            assert "role" in result
            assert "molecule" in result
            assert "raw_data" in result
            assert "analysis" in result
            assert "key_findings" in result
            assert "recommendations" in result
            assert result["agent_name"] == "IQVIA Insights Agent"
    
    def test_agent_key_findings(self, agent):
        """Test key findings extraction"""
        test_data = {
            "molecule": "Metformin",
            "market_size_usd_millions": 1500,
            "cagr_percent": 7.5,
            "competition": {"total_competitors": 8},
            "therapy_areas": ["Diabetes", "Cardiovascular"],
        }
        findings = agent._extract_key_findings(test_data)
        assert len(findings) > 0
        assert any("1500" in f or "Large" in f for f in findings)


class TestEXIMTradeAgent:
    """Tests for EXIM Trade Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return EXIMTradeAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "EXIM Trade Agent"
        assert agent.role == "Trade Intelligence Analyst"
        assert len(agent.tools) == 1
    
    def test_agent_analyze_structure(self, agent):
        """Test analyze method returns correct structure"""
        with patch.object(agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.content = "Test analysis of trade data"
            mock_agent.invoke.return_value = mock_response
            
            result = agent.analyze("Metformin")
            
            assert isinstance(result, dict)
            assert result["agent_name"] == "EXIM Trade Agent"
            assert "key_findings" in result
            assert "recommendations" in result


class TestPatentLandscapeAgent:
    """Tests for Patent Landscape Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return PatentLandscapeAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Patent Landscape Agent"
        assert agent.role == "Patent Intelligence Analyst"
        assert len(agent.tools) == 1
    
    def test_agent_analyze_structure(self, agent):
        """Test analyze method returns correct structure"""
        with patch.object(agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.content = "Test analysis of patent data"
            mock_agent.invoke.return_value = mock_response
            
            result = agent.analyze("Metformin")
            
            assert isinstance(result, dict)
            assert result["agent_name"] == "Patent Landscape Agent"
            assert "fto_assessment" in result.get("raw_data", {})


class TestClinicalTrialsAgent:
    """Tests for Clinical Trials Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return ClinicalTrialsAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Clinical Trials Agent"
        assert agent.role == "Clinical Research Analyst"
        assert len(agent.tools) == 1
    
    def test_agent_analyze_structure(self, agent):
        """Test analyze method returns correct structure"""
        with patch.object(agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.content = "Test analysis of trial data"
            mock_agent.invoke.return_value = mock_response
            
            result = agent.analyze("Metformin")
            
            assert isinstance(result, dict)
            assert result["agent_name"] == "Clinical Trials Agent"
            assert "trials" in result.get("raw_data", {})


class TestInternalInsightsAgent:
    """Tests for Internal Insights Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return InternalInsightsAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Internal Insights Agent"
        assert agent.role == "Strategic Intelligence Analyst"
        assert len(agent.tools) == 1
    
    def test_agent_analyze_structure(self, agent):
        """Test analyze method returns correct structure"""
        with patch.object(agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.content = "Test analysis of internal data"
            mock_agent.invoke.return_value = mock_response
            
            result = agent.analyze("Metformin")
            
            assert isinstance(result, dict)
            assert result["agent_name"] == "Internal Insights Agent"
            assert "documents" in result.get("raw_data", {})


class TestWebIntelligenceAgent:
    """Tests for Web Intelligence Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return WebIntelligenceAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.name == "Web Intelligence Agent"
        assert agent.role == "Scientific Intelligence Analyst"
        assert len(agent.tools) == 1
    
    def test_agent_analyze_structure(self, agent):
        """Test analyze method returns correct structure"""
        with patch.object(agent, 'agent') as mock_agent:
            mock_response = Mock()
            mock_response.content = "Test analysis of web data"
            mock_agent.invoke.return_value = mock_response
            
            result = agent.analyze("Metformin")
            
            assert isinstance(result, dict)
            assert result["agent_name"] == "Web Intelligence Agent"
            assert "results" in result.get("raw_data", {})


class TestAgentsIntegration:
    """Integration tests for all agents"""
    
    def test_all_agents_importable(self):
        """Test that all agents can be imported"""
        assert len(ALL_WORKER_AGENTS) == 6
    
    def test_all_agents_instantiable(self):
        """Test that all agents can be instantiated"""
        # Mock LLM to avoid API calls during testing
        with patch('src.agents.base_agent.get_llm') as mock_llm:
            mock_llm.return_value = Mock()
            
            for agent_class in ALL_WORKER_AGENTS:
                agent = agent_class()
                assert agent is not None
                assert hasattr(agent, 'name')
                assert hasattr(agent, 'role')
                assert hasattr(agent, 'analyze')
    
    def test_agent_consistency(self):
        """Test that all agents have consistent structure"""
        with patch('src.agents.base_agent.get_llm') as mock_llm:
            mock_llm.return_value = Mock()
            
            for agent_class in ALL_WORKER_AGENTS:
                agent = agent_class()
                
                # All agents should have these attributes
                assert hasattr(agent, 'name')
                assert hasattr(agent, 'role')
                assert hasattr(agent, 'tools')
                assert hasattr(agent, 'analyze')
                assert hasattr(agent, '_extract_key_findings')
                assert hasattr(agent, '_generate_recommendations')
                
                # All agents should have at least one tool
                assert len(agent.tools) > 0

