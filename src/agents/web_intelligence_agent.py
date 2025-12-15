"""
Web Intelligence Agent - Specialized web research analyst.
Analyzes scientific publications, guidelines, and market news.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .base_agent import BaseWorkerAgent, get_llm
from src.tools import web_intelligence_tool, get_web_data_raw


class WebIntelligenceAgent(BaseWorkerAgent):
    """
    Web intelligence agent specializing in scientific literature and market news analysis.
    """
    
    def __init__(self, llm=None):
        system_prompt = """You are a Senior Scientific Intelligence Analyst specializing in pharmaceutical literature and market intelligence.

Your expertise includes:
- Scientific publication analysis
- Clinical guideline interpretation
- Regulatory news assessment
- Market intelligence synthesis

When analyzing web intelligence:
1. Identify key scientific evidence and publications
2. Assess clinical guideline recommendations
3. Evaluate regulatory developments
4. Synthesize market intelligence and news
5. Provide evidence-based insights for repurposing

Always focus on identifying evidence-based repurposing opportunities from scientific literature and market intelligence."""
        
        super().__init__(
            name="Web Intelligence Agent",
            role="Scientific Intelligence Analyst",
            system_prompt=system_prompt,
            tools=[web_intelligence_tool],
            llm=llm
        )
    
    def analyze(self, molecule: str, target_indication: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze web intelligence for a molecule.
        
        Args:
            molecule: Name of the molecule
            target_indication: Optional target indication filter
            context: Optional additional context
            
        Returns:
            Structured web intelligence insights
        """
        # Get raw data from tool
        raw_data = get_web_data_raw(molecule, target_indication)
        
        # Get tool output for LLM context
        tool_output = web_intelligence_tool.invoke({"molecule": molecule, "target_indication": target_indication})
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following web intelligence data for {molecule}:

{tool_output}

Based on this data, provide:
1. Key scientific evidence and publication insights
2. Clinical guideline recommendations
3. Regulatory developments and news
4. Market intelligence synthesis
5. Evidence-based recommendations for repurposing

Focus on identifying evidence-based repurposing opportunities from scientific literature and market intelligence."""
        
        # Get LLM analysis
        messages = self.prompt_template.format_messages(input=analysis_prompt)
        response = self.agent.invoke(messages)
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        return self.format_insights(raw_data, analysis)
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key web intelligence findings"""
        findings = []
        
        total_results = data.get("total_results", 0)
        by_source_type = data.get("by_source_type", {})
        results = data.get("results", [])
        
        findings.append(f"Total sources found: {total_results}")
        
        if by_source_type:
            top_source_type = max(by_source_type.items(), key=lambda x: x[1])
            findings.append(f"Primary source type: {top_source_type[0]} ({top_source_type[1]} results)")
        
        # Count recent publications
        recent_pubs = len([r for r in results if "2024" in r.get("date", "")])
        if recent_pubs > 0:
            findings.append(f"Recent publications (2024): {recent_pubs}")
        
        # Identify source types
        source_types = list(by_source_type.keys())
        if source_types:
            findings.append(f"Source types: {', '.join(source_types[:3])}")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate web intelligence-based recommendations"""
        recommendations = []
        
        total_results = data.get("total_results", 0)
        by_source_type = data.get("by_source_type", {})
        results = data.get("results", [])
        
        if total_results > 20:
            recommendations.append("Strong evidence base - multiple sources support repurposing potential")
        elif total_results > 10:
            recommendations.append("Moderate evidence base - sufficient sources for evaluation")
        else:
            recommendations.append("Limited evidence base - may require additional research")
        
        # Check for scientific publications
        if "Scientific Publication" in by_source_type:
            pub_count = by_source_type["Scientific Publication"]
            if pub_count > 5:
                recommendations.append("Strong scientific publication support - evidence-based opportunity")
        
        # Check for guidelines
        if "Clinical Guideline" in by_source_type:
            recommendations.append("Clinical guidelines available - regulatory pathway support")
        
        # Check for regulatory news
        if "Regulatory News" in by_source_type:
            recommendations.append("Regulatory developments identified - monitor for opportunities")
        
        # Recent publications
        recent_pubs = len([r for r in results if "2024" in r.get("date", "")])
        if recent_pubs > 5:
            recommendations.append("High recent publication activity - active research area")
        
        return recommendations

