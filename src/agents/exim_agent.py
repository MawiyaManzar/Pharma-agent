"""
EXIM Trade Agent - Specialized trade and supply chain analyst.
Analyzes import/export data and supply chain risks.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .base_agent import BaseWorkerAgent, get_llm
from src.tools import exim_trade_tool, get_exim_data_raw


class EXIMTradeAgent(BaseWorkerAgent):
    """
    Trade intelligence agent specializing in import/export and supply chain analysis.
    """
    
    def __init__(self, llm=None):
        system_prompt = """You are a Senior Trade Intelligence Analyst specializing in pharmaceutical supply chain and trade dynamics.

Your expertise includes:
- Import/export trade flow analysis
- Supply chain risk assessment
- Formulation movement tracking
- Trade dependency evaluation

When analyzing trade data:
1. Assess import dependency and supply chain vulnerabilities
2. Identify key supplier countries and risk zones
3. Evaluate formulation availability and trade patterns
4. Provide supply chain risk mitigation recommendations

Always focus on identifying supply chain opportunities and risks for repurposing decisions."""
        
        super().__init__(
            name="EXIM Trade Agent",
            role="Trade Intelligence Analyst",
            system_prompt=system_prompt,
            tools=[exim_trade_tool],
            llm=llm
        )
    
    def analyze(self, molecule: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze trade intelligence for a molecule.
        
        Args:
            molecule: Name of the molecule
            context: Optional additional context
            
        Returns:
            Structured trade insights
        """
        # Get raw data from tool
        raw_data = get_exim_data_raw(molecule)
        
        # Get tool output for LLM context
        tool_output = exim_trade_tool.invoke({"molecule": molecule})
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following trade intelligence data for {molecule}:

{tool_output}

Based on this data, provide:
1. Supply chain risk assessment
2. Import dependency analysis
3. Key supplier country evaluation
4. Formulation availability insights
5. Strategic recommendations for supply chain security

Focus on identifying supply chain opportunities and risks for repurposing initiatives."""
        
        # Get LLM analysis
        messages = self.prompt_template.format_messages(input=analysis_prompt)
        response = self.agent.invoke(messages)
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        return self.format_insights(raw_data, analysis)
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key trade findings"""
        findings = []
        
        import_dep = data.get("import_dependency_percent", 0)
        risk_level = data.get("risk_level", "")
        exporters = data.get("top_exporters", [])
        formulations = data.get("formulations", [])
        
        findings.append(f"Import dependency: {import_dep}%")
        findings.append(f"Supply chain risk: {risk_level}")
        
        if exporters:
            top_exporter = exporters[0].get("country", "Unknown")
            findings.append(f"Primary exporter: {top_exporter}")
        
        if formulations:
            findings.append(f"Available formulations: {', '.join(formulations[:3])}")
        
        trade_trend = data.get("trade_trend", "")
        if trade_trend:
            findings.append(f"Trade trend: {trade_trend}")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate trade-based recommendations"""
        recommendations = []
        
        import_dep = data.get("import_dependency_percent", 0)
        risk_level = data.get("risk_level", "")
        risk_zones = data.get("risk_zones", [])
        
        if import_dep > 70:
            recommendations.append("High import dependency - consider local manufacturing or alternative suppliers")
        elif import_dep > 50:
            recommendations.append("Moderate import dependency - diversify supplier base")
        else:
            recommendations.append("Low import dependency - favorable supply chain position")
        
        if risk_level == "High" and risk_zones:
            recommendations.append(f"High-risk zones identified: {', '.join(risk_zones)} - develop mitigation strategy")
        elif risk_level == "Medium":
            recommendations.append("Monitor supply chain risks and maintain backup suppliers")
        
        formulations = data.get("formulations", [])
        if len(formulations) > 3:
            recommendations.append("Multiple formulations available - consider formulation-specific repurposing")
        
        return recommendations

