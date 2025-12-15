"""
Internal Insights Agent - Specialized internal document analyst.
Analyzes internal strategy, documents, and field intelligence.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .base_agent import BaseWorkerAgent, get_llm
from src.tools import internal_insights_tool, get_internal_data_raw


class InternalInsightsAgent(BaseWorkerAgent):
    """
    Internal intelligence agent specializing in internal document and strategy analysis.
    """
    
    def __init__(self, llm=None):
        system_prompt = """You are a Senior Strategic Intelligence Analyst specializing in internal pharmaceutical company intelligence.

Your expertise includes:
- Internal strategy document analysis
- Field intelligence interpretation
- Portfolio alignment assessment
- Strategic priority evaluation

When analyzing internal data:
1. Assess strategy alignment and priority levels
2. Extract key takeaways from internal documents
3. Evaluate field intelligence and market signals
4. Provide strategic recommendations aligned with internal priorities

Always focus on aligning repurposing opportunities with internal strategy and priorities."""
        
        super().__init__(
            name="Internal Insights Agent",
            role="Strategic Intelligence Analyst",
            system_prompt=system_prompt,
            tools=[internal_insights_tool],
            llm=llm
        )
    
    def analyze(self, molecule: str, document_filter: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze internal insights for a molecule.
        
        Args:
            molecule: Name of the molecule
            document_filter: Optional document type filter
            context: Optional additional context
            
        Returns:
            Structured internal insights
        """
        # Get raw data from tool
        raw_data = get_internal_data_raw(molecule, document_filter)
        
        # Get tool output for LLM context
        tool_output = internal_insights_tool.invoke({"molecule": molecule, "document_filter": document_filter})
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following internal intelligence data for {molecule}:

{tool_output}

Based on this data, provide:
1. Strategy alignment assessment
2. Internal priority level evaluation
3. Key strategic takeaways
4. Field intelligence insights
5. Strategic recommendations aligned with internal priorities

Focus on aligning repurposing opportunities with internal strategy and priorities."""
        
        # Get LLM analysis
        messages = self.prompt_template.format_messages(input=analysis_prompt)
        response = self.agent.invoke(messages)
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        return self.format_insights(raw_data, analysis)
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key internal findings"""
        findings = []
        
        strategy_alignment = data.get("strategy_alignment", "")
        priority_level = data.get("priority_level", "")
        total_docs = data.get("total_documents", 0)
        field_insights = data.get("field_insights", [])
        
        findings.append(f"Strategy alignment: {strategy_alignment}")
        findings.append(f"Priority level: {priority_level}")
        findings.append(f"Internal documents reviewed: {total_docs}")
        
        if field_insights:
            findings.append(f"Field intelligence points: {len(field_insights)}")
        
        documents = data.get("documents", [])
        if documents:
            top_dept = max(set(doc.get("department", "") for doc in documents), 
                          key=lambda x: sum(1 for d in documents if d.get("department") == x))
            findings.append(f"Primary department: {top_dept}")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate internal strategy-based recommendations"""
        recommendations = []
        
        strategy_alignment = data.get("strategy_alignment", "")
        priority_level = data.get("priority_level", "")
        field_insights = data.get("field_insights", [])
        
        if strategy_alignment == "High":
            recommendations.append("Strong strategy alignment - prioritize this repurposing opportunity")
        elif strategy_alignment == "Medium":
            recommendations.append("Moderate strategy alignment - evaluate fit with strategic priorities")
        else:
            recommendations.append("Low strategy alignment - may require strategic review")
        
        if "Top Priority" in priority_level or "Active Development" in priority_level:
            recommendations.append("High internal priority - allocate resources accordingly")
        elif "Medium Priority" in priority_level:
            recommendations.append("Moderate priority - monitor and evaluate progress")
        
        if field_insights:
            recommendations.append("Field intelligence available - incorporate market signals into strategy")
        
        if strategy_alignment == "High" and "Top Priority" in priority_level:
            recommendations.append("Strong alignment and priority - fast-track repurposing initiative")
        
        return recommendations

