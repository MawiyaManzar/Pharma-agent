"""
Tests for report generation.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.reports import ReportGenerator


class TestReportGenerator:
    """Tests for Report Generator"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def report_generator(self, temp_output_dir):
        """Create report generator instance"""
        return ReportGenerator(output_dir=temp_output_dir)
    
    @pytest.fixture
    def sample_report_data(self):
        """Sample report data for testing"""
        return {
            "molecule": "Metformin",
            "query": "Analyze repurposing opportunities for Metformin",
            "synthesis": "Metformin shows strong potential for repurposing in multiple therapeutic areas. Market analysis indicates growing demand, and clinical trials show active research in new indications.",
            "key_findings": [
                "Market size: $1500M USD",
                "CAGR: 7.5%",
                "15 active clinical trials",
                "FTO Status: Green (Low risk)",
            ],
            "recommendations": [
                "Proceed with repurposing initiative",
                "Focus on diabetes and cardiovascular indications",
                "Monitor patent landscape",
            ],
            "agent_results": {
                "iqvia": {
                    "agent_name": "IQVIA Insights Agent",
                    "key_findings": ["Large market size"],
                    "recommendations": ["High growth opportunity"],
                    "status": "completed"
                },
                "exim": {
                    "agent_name": "EXIM Trade Agent",
                    "key_findings": ["Low import dependency"],
                    "recommendations": ["Favorable supply chain"],
                    "status": "completed"
                }
            },
            "summary": {
                "total_agents_executed": 6,
                "agents_failed": 0,
                "key_insights_count": 4,
                "recommendations_count": 3,
            }
        }
    
    def test_report_generator_initialization(self, report_generator, temp_output_dir):
        """Test report generator initializes correctly"""
        assert report_generator.output_dir == Path(temp_output_dir)
        assert report_generator.output_dir.exists()
    
    def test_generate_pdf_report(self, report_generator, sample_report_data):
        """Test PDF report generation"""
        pdf_path = report_generator.generate_pdf_report(sample_report_data)
        
        assert Path(pdf_path).exists()
        assert pdf_path.endswith(".pdf")
        assert "Metformin" in pdf_path
    
    def test_generate_excel_report(self, report_generator, sample_report_data):
        """Test Excel report generation"""
        excel_path = report_generator.generate_excel_report(sample_report_data)
        
        assert Path(excel_path).exists()
        assert excel_path.endswith(".xlsx")
        assert "Metformin" in excel_path
    
    def test_generate_both_reports(self, report_generator, sample_report_data):
        """Test generating both PDF and Excel reports"""
        result = report_generator.generate_reports(sample_report_data)
        
        assert "pdf" in result
        assert "excel" in result
        assert Path(result["pdf"]).exists()
        assert Path(result["excel"]).exists()
        assert "base_filename" in result
    
    def test_custom_filename(self, report_generator, sample_report_data):
        """Test custom filename"""
        custom_name = "Custom_Report_Test"
        result = report_generator.generate_reports(sample_report_data, base_filename=custom_name)
        
        assert custom_name in result["pdf"]
        assert custom_name in result["excel"]
        assert result["base_filename"] == custom_name
    
    def test_report_with_minimal_data(self, report_generator):
        """Test report generation with minimal data"""
        minimal_data = {
            "molecule": "TestMolecule",
            "query": "Test query",
            "synthesis": "Test synthesis",
        }
        
        pdf_path = report_generator.generate_pdf_report(minimal_data)
        excel_path = report_generator.generate_excel_report(minimal_data)
        
        assert Path(pdf_path).exists()
        assert Path(excel_path).exists()




