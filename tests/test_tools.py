"""
Tests for all mock tools.
"""

import pytest
from src.tools import (
    iqvia_insights_tool,
    exim_trade_tool,
    patent_landscape_tool,
    clinical_trials_tool,
    internal_insights_tool,
    web_intelligence_tool,
    get_iqvia_data_raw,
    get_exim_data_raw,
    get_patent_data_raw,
    get_clinical_trials_data_raw,
    get_internal_data_raw,
    get_web_data_raw,
)


class TestIQVIATool:
    """Tests for IQVIA Insights Tool"""
    
    def test_iqvia_tool_returns_string(self):
        """Test that tool returns formatted string"""
        result = iqvia_insights_tool.invoke({"molecule": "Metformin"})
        assert isinstance(result, str)
        assert "Metformin" in result
        assert "Market Size" in result or "market" in result.lower()
    
    def test_iqvia_raw_data_structure(self):
        """Test that raw data has expected structure"""
        data = get_iqvia_data_raw("Metformin")
        assert "molecule" in data
        assert "market_size_usd_millions" in data
        assert "cagr_percent" in data
        assert "competition" in data
        assert "therapy_areas" in data
    
    def test_iqvia_with_region(self):
        """Test tool with region parameter"""
        result = iqvia_insights_tool.invoke({"molecule": "Aspirin", "region": "US"})
        assert "Aspirin" in result
        assert "US" in result or "Global" in result


class TestEXIMTool:
    """Tests for EXIM Trade Tool"""
    
    def test_exim_tool_returns_string(self):
        """Test that tool returns formatted string"""
        result = exim_trade_tool.invoke({"molecule": "Metformin"})
        assert isinstance(result, str)
        assert "Metformin" in result
        assert "Import" in result or "Export" in result
    
    def test_exim_raw_data_structure(self):
        """Test that raw data has expected structure"""
        data = get_exim_data_raw("Metformin")
        assert "molecule" in data
        assert "import_dependency_percent" in data
        assert "risk_level" in data
        assert "top_exporters" in data
        assert "top_importers" in data


class TestPatentTool:
    """Tests for Patent Landscape Tool"""
    
    def test_patent_tool_returns_string(self):
        """Test that tool returns formatted string"""
        result = patent_landscape_tool.invoke({"molecule": "Metformin"})
        assert isinstance(result, str)
        assert "Metformin" in result
        assert "Patent" in result or "FTO" in result
    
    def test_patent_raw_data_structure(self):
        """Test that raw data has expected structure"""
        data = get_patent_data_raw("Metformin")
        assert "molecule" in data
        assert "total_patents" in data
        assert "active_patents" in data
        assert "fto_assessment" in data
        assert data["fto_assessment"]["status"] in ["Green", "Amber", "Red"]


class TestClinicalTrialsTool:
    """Tests for Clinical Trials Tool"""
    
    def test_clinical_trials_tool_returns_string(self):
        """Test that tool returns formatted string"""
        result = clinical_trials_tool.invoke({"molecule": "Metformin"})
        assert isinstance(result, str)
        assert "Metformin" in result
        assert "Trial" in result or "trial" in result.lower()
    
    def test_clinical_trials_raw_data_structure(self):
        """Test that raw data has expected structure"""
        data = get_clinical_trials_data_raw("Metformin")
        assert "molecule" in data
        assert "total_trials" in data
        assert "ongoing_trials" in data
        assert "trials" in data
        assert "phase_distribution" in data


class TestInternalInsightsTool:
    """Tests for Internal Insights Tool"""
    
    def test_internal_insights_tool_returns_string(self):
        """Test that tool returns formatted string"""
        result = internal_insights_tool.invoke({"molecule": "Metformin"})
        assert isinstance(result, str)
        assert "Metformin" in result
    
    def test_internal_insights_raw_data_structure(self):
        """Test that raw data has expected structure"""
        data = get_internal_data_raw("Metformin")
        assert "molecule" in data
        assert "total_documents" in data
        assert "documents" in data
        assert "strategy_alignment" in data


class TestWebIntelligenceTool:
    """Tests for Web Intelligence Tool"""
    
    def test_web_intelligence_tool_returns_string(self):
        """Test that tool returns formatted string"""
        result = web_intelligence_tool.invoke({"molecule": "Metformin"})
        assert isinstance(result, str)
        assert "Metformin" in result
    
    def test_web_intelligence_raw_data_structure(self):
        """Test that raw data has expected structure"""
        data = get_web_data_raw("Metformin")
        assert "molecule" in data
        assert "total_results" in data
        assert "results" in data
        assert "by_source_type" in data


class TestToolsIntegration:
    """Integration tests for all tools"""
    
    def test_all_tools_importable(self):
        """Test that all tools can be imported"""
        from src.tools import ALL_TOOLS
        assert len(ALL_TOOLS) == 6
    
    def test_all_tools_callable(self):
        """Test that all tools can be invoked"""
        test_molecule = "TestMolecule"
        
        # Test all tools with same molecule
        iqvia_result = iqvia_insights_tool.invoke({"molecule": test_molecule})
        exim_result = exim_trade_tool.invoke({"molecule": test_molecule})
        patent_result = patent_landscape_tool.invoke({"molecule": test_molecule})
        trials_result = clinical_trials_tool.invoke({"molecule": test_molecule})
        internal_result = internal_insights_tool.invoke({"molecule": test_molecule})
        web_result = web_intelligence_tool.invoke({"molecule": test_molecule})
        
        # All should return strings
        assert all(isinstance(r, str) for r in [
            iqvia_result, exim_result, patent_result,
            trials_result, internal_result, web_result
        ])
        
        # All should mention the molecule
        assert all(test_molecule in r for r in [
            iqvia_result, exim_result, patent_result,
            trials_result, internal_result, web_result
        ])

