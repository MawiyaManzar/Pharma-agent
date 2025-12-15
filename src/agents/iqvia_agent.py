"""
IQVIA Insights Agent - Specialized market intelligence analyst.
Analyzes market size, competition, and growth opportunities.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .base_agent import BaseWorkerAgent, get_llm
from src.tools import iqvia_insights_tool, get_iqvia_data_raw


class IQVIAInsightsAgent(BaseWorkerAgent):
    """
    Market intelligence agent specializing in IQVIA data analysis.
    """
    
    def __init__(self, llm=None):
        system_prompt = """You are a Senior Market Intelligence Analyst specializing in pharmaceutical market research.

Your expertise includes:
- Market size and growth analysis
- Competitive landscape assessment
- Therapy area market dynamics
- Market trend identification

When analyzing market data:
1. Identify market opportunities and growth potential
2. Assess competitive intensity and market concentration
3. Highlight therapy areas with high growth potential
4. Provide actionable market insights for drug repurposing decisions

Always be specific, data-driven, and focus on repurposing opportunities."""
        
        super().__init__(
            name="IQVIA Insights Agent",
            role="Market Intelligence Analyst",
            system_prompt=system_prompt,
            tools=[iqvia_insights_tool],
            llm=llm
        )
    
    def analyze(self, molecule: str, region: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze market intelligence for a molecule.
        
        Args:
            molecule: Name of the molecule
            region: Optional region filter
            context: Optional additional context
            
        Returns:
            Structured market insights
        """
        # Get raw data from tool
        raw_data = get_iqvia_data_raw(molecule, region)
        
        # Get tool output for LLM context
        tool_output = iqvia_insights_tool.invoke({"molecule": molecule, "region": region})
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following market intelligence data for {molecule}:

{tool_output}

Based on this data, provide:
1. Market opportunity assessment (size, growth potential)
2. Competitive landscape analysis
3. Key therapy areas and their market dynamics
4. Repurposing opportunity insights
5. Strategic recommendations

Focus on identifying repurposing opportunities based on market gaps and growth trends."""
        
        # Get LLM analysis
        messages = self.prompt_template.format_messages(input=analysis_prompt)
        response = self.agent.invoke(messages)
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        return self.format_insights(raw_data, analysis)
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key market findings"""
        findings = []
        
        market_size = data.get("market_size_usd_millions", 0)
        cagr = data.get("cagr_percent", 0)
        competition = data.get("competition", {})
        
        if market_size > 1000:
            findings.append(f"Large market size: ${market_size}M USD")
        elif market_size > 500:
            findings.append(f"Moderate market size: ${market_size}M USD")
        else:
            findings.append(f"Emerging market: ${market_size}M USD")
        
        if cagr > 5:
            findings.append(f"Strong growth trajectory: {cagr}% CAGR")
        elif cagr > 0:
            findings.append(f"Stable growth: {cagr}% CAGR")
        else:
            findings.append(f"Declining market: {cagr}% CAGR")
        
        comp_count = competition.get("total_competitors", 0)
        if comp_count < 5:
            findings.append(f"Low competition: {comp_count} competitors")
        elif comp_count < 15:
            findings.append(f"Moderate competition: {comp_count} competitors")
        else:
            findings.append(f"High competition: {comp_count} competitors")
        
        therapy_areas = data.get("therapy_areas", [])
        if therapy_areas:
            findings.append(f"Key therapy areas: {', '.join(therapy_areas)}")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate market-based recommendations"""
        recommendations = []
        
        cagr = data.get("cagr_percent", 0)
        market_trend = data.get("market_trend", "")
        competition = data.get("competition", {})
        comp_count = competition.get("total_competitors", 0)
        
        if cagr > 5 and comp_count < 10:
            recommendations.append("High-growth, low-competition market - strong repurposing opportunity")
        elif cagr > 0 and market_trend == "Growing":
            recommendations.append("Growing market with potential for new indications")
        
        if comp_count > 20:
            recommendations.append("Highly competitive market - focus on niche indications or formulations")
        
        therapy_areas = data.get("therapy_areas", [])
        if len(therapy_areas) > 1:
            recommendations.append(f"Multiple therapy areas suggest cross-indication repurposing potential")
        
        return recommendations

