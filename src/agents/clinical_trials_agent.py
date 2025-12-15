"""
Clinical Trials Agent - Specialized clinical trial analyst.
Analyzes ongoing and completed trials, identifies emerging indications.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .base_agent import BaseWorkerAgent, get_llm
from src.tools import clinical_trials_tool, get_clinical_trials_data_raw


class ClinicalTrialsAgent(BaseWorkerAgent):
    """
    Clinical trial intelligence agent specializing in trial data analysis.
    """
    
    def __init__(self, llm=None):
        system_prompt = """You are a Senior Clinical Research Analyst specializing in pharmaceutical clinical trial intelligence.

Your expertise includes:
- Clinical trial landscape analysis
- Phase distribution and trial status
- Emerging indication identification
- Trial outcome assessment

When analyzing trial data:
1. Identify ongoing trials and their phases
2. Assess emerging indications with active research
3. Evaluate trial distribution across phases
4. Provide insights on research momentum and opportunities

Always focus on identifying repurposing opportunities based on active research and emerging indications."""
        
        super().__init__(
            name="Clinical Trials Agent",
            role="Clinical Research Analyst",
            system_prompt=system_prompt,
            tools=[clinical_trials_tool],
            llm=llm
        )
    
    def analyze(self, molecule: str, mechanism: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze clinical trial data for a molecule.
        
        Args:
            molecule: Name of the molecule
            mechanism: Optional mechanism of action filter
            context: Optional additional context
            
        Returns:
            Structured trial insights
        """
        # Get raw data from tool
        raw_data = get_clinical_trials_data_raw(molecule, mechanism)
        
        # Get tool output for LLM context
        tool_output = clinical_trials_tool.invoke({"molecule": molecule, "mechanism": mechanism})
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following clinical trial data for {molecule}:

{tool_output}

Based on this data, provide:
1. Research momentum assessment (ongoing vs completed trials)
2. Emerging indication identification
3. Phase distribution analysis
4. Geographic trial distribution
5. Strategic recommendations for repurposing opportunities

Focus on identifying repurposing opportunities based on active research and emerging indications."""
        
        # Get LLM analysis
        messages = self.prompt_template.format_messages(input=analysis_prompt)
        response = self.agent.invoke(messages)
        analysis = response.content if hasattr(response, 'content') else str(response)
        
        return self.format_insights(raw_data, analysis)
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key trial findings"""
        findings = []
        
        total_trials = data.get("total_trials", 0)
        ongoing_trials = data.get("ongoing_trials", 0)
        completed_trials = data.get("completed_trials", 0)
        phase_dist = data.get("phase_distribution", {})
        emerging_indications = data.get("emerging_indications", {})
        
        findings.append(f"Total trials: {total_trials} (Ongoing: {ongoing_trials}, Completed: {completed_trials})")
        
        if phase_dist:
            phase_summary = ", ".join([f"{phase}: {count}" for phase, count in phase_dist.items()])
            findings.append(f"Phase distribution: {phase_summary}")
        
        if emerging_indications:
            top_indication = max(emerging_indications.items(), key=lambda x: x[1])
            findings.append(f"Top emerging indication: {top_indication[0]} ({top_indication[1]} trials)")
        
        if ongoing_trials > 10:
            findings.append("High research activity - strong repurposing interest")
        elif ongoing_trials > 5:
            findings.append("Moderate research activity")
        else:
            findings.append("Limited ongoing research")
        
        return findings
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate trial-based recommendations"""
        recommendations = []
        
        ongoing_trials = data.get("ongoing_trials", 0)
        emerging_indications = data.get("emerging_indications", {})
        phase_dist = data.get("phase_distribution", {})
        
        if ongoing_trials > 10:
            recommendations.append("High research momentum - consider aligning with active research areas")
        
        if emerging_indications:
            top_indications = sorted(emerging_indications.items(), key=lambda x: x[1], reverse=True)[:3]
            indication_list = ", ".join([ind for ind, _ in top_indications])
            recommendations.append(f"Focus on emerging indications: {indication_list}")
        
        phase_2_count = phase_dist.get("Phase 2", 0)
        phase_3_count = phase_dist.get("Phase 3", 0)
        
        if phase_2_count > 0 or phase_3_count > 0:
            recommendations.append("Active Phase 2/3 trials indicate strong clinical validation potential")
        
        if not emerging_indications and ongoing_trials < 5:
            recommendations.append("Limited research activity - potential whitespace opportunity")
        
        return recommendations

