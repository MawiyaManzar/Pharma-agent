"""
Patent Landscape Agent - Specialized patent and FTO analyst.
Analyzes patent landscape and Freedom-To-Operate.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .base_agent import BaseWorkerAgent, get_llm
from src.tools import patent_landscape_tool, get_patent_data_raw


class PatentLandscapeAgent(BaseWorkerAgent):
    """
    Patent intelligence agent specializing in patent landscape and FTO analysis.
    """
    
    def __init__(self, llm=None):
        system_prompt = """You are a Senior Patent Analyst specializing in pharmaceutical intellectual property and Freedom-To-Operate (FTO) assessment.

Your expertise includes:
- Patent landscape analysis
- FTO risk assessment
- Patent expiry timeline evaluation
- IP strategy recommendations

When analyzing patent data:
1. Assess FTO status (Green/Amber/Red)
2. Identify blocking patents and expiry timelines
3. Evaluate patent landscape complexity
4. Provide IP strategy recommendations for repurposing

Always focus on identifying patent opportunities and risks for repurposing initiatives."""
        
        super().__init__(
            name="Patent Landscape Agent",
            role="Patent Intelligence Analyst",
            system_prompt=system_prompt,
            tools=[patent_landscape_tool],
            llm=llm
        )
    
    def analyze(self, molecule: str, therapy_area: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze patent landscape for a molecule.
        
        Args:
            molecule: Name of the molecule
            therapy_area: Optional therapy area filter
            context: Optional additional context
            
        Returns:
            Structured patent insights
        """
        # Get raw data from tool
        raw_data = get_patent_data_raw(molecule, therapy_area)
        
        # Get tool output for LLM context
        tool_output = patent_landscape_tool.invoke({"molecule": molecule, "therapy_area": therapy_area})
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following patent landscape data for {molecule}:

{tool_output}

Based on this data, provide:
1. FTO status assessment and risk level
2. Key blocking patents and their expiry timelines
3. Patent landscape complexity analysis
4. IP strategy recommendations for repurposing
5. Opportunities based on patent expiry windows

Focus on identifying patent opportunities and risks for repurposing initiatives."""
        
        # Get LLM analysis
        messages = self.prompt_template.format_messages(input=analysis_prompt)
        response = self.agent.invoke(messages)
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        return self.format_insights(raw_data, analysis)
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key patent findings"""
        findings = []
        
        fto_assessment = data.get("fto_assessment", {})
        fto_status = fto_assessment.get("status", "Unknown")
        fto_risk = fto_assessment.get("risk_level", "Unknown")
        active_patents = data.get("active_patents", 0)
        expired_patents = data.get("expired_patents", 0)
        upcoming_expiries = data.get("upcoming_expiries", 0)
        
        findings.append(f"FTO Status: {fto_status} ({fto_risk} risk)")
        findings.append(f"Active patents: {active_patents}, Expired: {expired_patents}")
        
        if upcoming_expiries > 0:
            findings.append(f"Patents expiring in next 5 years: {upcoming_expiries}")
        
        blocking_patents = fto_assessment.get("blocking_patents", [])
        if blocking_patents:
            findings.append(f"Blocking patents identified: {len(blocking_patents)}")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate patent-based recommendations"""
        recommendations = []
        
        fto_assessment = data.get("fto_assessment", {})
        fto_status = fto_assessment.get("status", "")
        fto_risk = fto_assessment.get("risk_level", "")
        upcoming_expiries = data.get("upcoming_expiries", 0)
        
        if fto_status == "Green":
            recommendations.append("Clear FTO path - proceed with repurposing initiatives")
        elif fto_status == "Amber":
            recommendations.append("Moderate FTO risk - consider licensing or design-around strategies")
        elif fto_status == "Red":
            recommendations.append("High FTO risk - require detailed IP analysis and potential licensing")
        
        if upcoming_expiries > 0:
            recommendations.append(f"{upcoming_expiries} patents expiring soon - plan for post-expiry opportunities")
        
        blocking_patents = fto_assessment.get("blocking_patents", [])
        if blocking_patents:
            recommendations.append("Review blocking patents for licensing opportunities or expiry dates")
        
        if fto_risk == "Low" and upcoming_expiries > 0:
            recommendations.append("Favorable IP landscape with upcoming expiries - strategic timing opportunity")
        
        return recommendations

