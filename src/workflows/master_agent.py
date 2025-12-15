"""
Master Agent - Orchestrates all worker agents and synthesizes results.
"""

from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

from src.agents import (
    IQVIAInsightsAgent,
    EXIMTradeAgent,
    PatentLandscapeAgent,
    ClinicalTrialsAgent,
    InternalInsightsAgent,
    WebIntelligenceAgent,
)

load_dotenv()


class MasterAgent:
    """
    Master Agent that orchestrates all worker agents and synthesizes results.
    
    The Master Agent acts as a Senior Pharmaceutical Strategy Director,
    coordinating a team of specialized analysts to provide comprehensive
    drug repurposing intelligence.
    
    Responsibilities:
    - Break down complex queries into specialized research tasks
    - Coordinate execution of 6 worker agents
    - Synthesize all findings into strategic narrative
    - Identify repurposing opportunities across multiple dimensions
    
    Example:
        >>> master = MasterAgent()
        >>> agents = master.determine_agents_to_run("Analyze Metformin", "Metformin")
        >>> result = master.execute_agent("iqvia", "Metformin")
        >>> synthesis = master.synthesize_results(results, "Metformin", "query")
    """
    
    def __init__(self):
        """
        Initialize Master Agent with all worker agents.
        
        Sets up:
        - Google GenAI LLM (Gemini 2.5 Flash)
        - All 6 worker agents (IQVIA, EXIM, Patent, Clinical Trials, Internal, Web)
        - System prompt for strategic analysis
        """
        # Initialize LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=api_key,
        )
        
        # Initialize all worker agents
        self.worker_agents = {
            "iqvia": IQVIAInsightsAgent(),
            "exim": EXIMTradeAgent(),
            "patent": PatentLandscapeAgent(),
            "clinical_trials": ClinicalTrialsAgent(),
            "internal": InternalInsightsAgent(),
            "web": WebIntelligenceAgent(),
        }
        
        # System prompt for Master Agent
        self.system_prompt = """You are a Senior Pharmaceutical Strategy Director orchestrating a team of specialized analysts.

Your role is to:
1. Break down complex drug repurposing queries into specialized research tasks
2. Coordinate a team of expert analysts (Market, Trade, Patent, Clinical Trials, Internal, Web Intelligence)
3. Synthesize all findings into a coherent strategic narrative
4. Identify repurposing opportunities based on:
   - Unmet clinical needs
   - Research momentum (active trials)
   - New indication opportunities
   - Patent/FTO landscape
   - Market potential
   - Supply chain considerations

Always provide strategic, actionable insights for drug repurposing decisions."""
    
    def determine_agents_to_run(self, query: str, molecule: str) -> List[str]:
        """
        Determine which agents should run based on the query.
        
        Args:
            query: User query
            molecule: Molecule name
            
        Returns:
            List of agent names to execute
        """
        query_lower = query.lower()
        
        # Default: run all agents for comprehensive analysis
        agents_to_run = list(self.worker_agents.keys())
        
        # If query is specific, we could filter agents, but for now run all
        # This ensures comprehensive analysis
        
        return agents_to_run
    
    def execute_agent(self, agent_name: str, molecule: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a specific worker agent.
        
        Args:
            agent_name: Name of the agent to execute
            molecule: Molecule name
            context: Optional context (region, indication, etc.)
            
        Returns:
            Agent result dictionary
        """
        agent = self.worker_agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        try:
            # Execute agent based on type
            if agent_name == "iqvia":
                region = context.get("region") if context else None
                result = agent.analyze(molecule, region=region, context=context)
            elif agent_name == "patent":
                therapy_area = context.get("therapy_area") if context else None
                result = agent.analyze(molecule, therapy_area=therapy_area, context=context)
            elif agent_name == "clinical_trials":
                mechanism = context.get("mechanism") if context else None
                result = agent.analyze(molecule, mechanism=mechanism, context=context)
            elif agent_name == "internal":
                doc_filter = context.get("document_filter") if context else None
                result = agent.analyze(molecule, document_filter=doc_filter, context=context)
            elif agent_name == "web":
                target_indication = context.get("target_indication") if context else None
                result = agent.analyze(molecule, target_indication=target_indication, context=context)
            else:
                # EXIM and others
                result = agent.analyze(molecule, context=context)
            
            return result
        except Exception as e:
            return {
                "agent_name": agent.name,
                "error": str(e),
                "status": "failed"
            }
    
    def synthesize_results(self, results: Dict[str, Dict[str, Any]], molecule: str, query: str) -> Dict[str, Any]:
        """
        Synthesize all agent results into a coherent narrative.
        
        Args:
            results: Dictionary of agent results
            molecule: Molecule name
            query: Original user query
            
        Returns:
            Synthesized result dictionary
        """
        # Collect all analyses and key findings
        all_analyses = []
        all_findings = []
        all_recommendations = []
        
        for agent_name, result in results.items():
            if result.get("status") == "failed":
                continue
            
            agent_name_display = result.get("agent_name", agent_name)
            analysis = result.get("analysis", "")
            findings = result.get("key_findings", [])
            recommendations = result.get("recommendations", [])
            
            if analysis:
                all_analyses.append(f"**{agent_name_display}**:\n{analysis}")
            if findings:
                all_findings.extend([f"{agent_name_display}: {f}" for f in findings])
            if recommendations:
                all_recommendations.extend([f"{agent_name_display}: {r}" for r in recommendations])
        
        # Create synthesis prompt template (NOT an f-string - use placeholders)
        synthesis_prompt_template = """Synthesize the following comprehensive analysis for {molecule}:

User Query: {query}

**Market Intelligence (IQVIA)**:
{iqvia_analysis}

**Trade Intelligence (EXIM)**:
{exim_analysis}

**Patent Landscape**:
{patent_analysis}

**Clinical Trials**:
{clinical_trials_analysis}

**Internal Insights**:
{internal_analysis}

**Web Intelligence**:
{web_analysis}

Based on all this intelligence, provide:
1. **Executive Summary**: High-level repurposing opportunity assessment
2. **Unmet Clinical Needs**: Identify gaps in current treatment landscape
3. **Research Momentum**: Active trials and emerging indications
4. **New Indication Opportunities**: Specific repurposing opportunities
5. **Patent/FTO Analysis**: IP landscape and freedom to operate
6. **Market Potential**: Market size, growth, and competition
7. **Strategic Recommendations**: Actionable next steps for repurposing

Format as a comprehensive strategic report suitable for executive decision-making."""
        
        # Get LLM synthesis
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompt),
            HumanMessagePromptTemplate.from_template(synthesis_prompt_template),
        ])
        
        # Format with actual values - this will properly escape any curly braces
        messages = prompt_template.format_messages(
            molecule=molecule,
            query=query,
            iqvia_analysis=results.get('iqvia', {}).get('analysis', 'N/A'),
            exim_analysis=results.get('exim', {}).get('analysis', 'N/A'),
            patent_analysis=results.get('patent', {}).get('analysis', 'N/A'),
            clinical_trials_analysis=results.get('clinical_trials', {}).get('analysis', 'N/A'),
            internal_analysis=results.get('internal', {}).get('analysis', 'N/A'),
            web_analysis=results.get('web', {}).get('analysis', 'N/A'),
        )
        
        response = self.llm.invoke(messages)
        synthesis = response.content if hasattr(response, 'content') else str(response)
        
        # Build synthesized result
        synthesized_result = {
            "molecule": molecule,
            "query": query,
            "synthesis": synthesis,
            "key_findings": all_findings,
            "recommendations": all_recommendations,
            "agent_results": results,
            "summary": {
                "total_agents_executed": len([r for r in results.values() if r.get("status") != "failed"]),
                "agents_failed": len([r for r in results.values() if r.get("status") == "failed"]),
                "key_insights_count": len(all_findings),
                "recommendations_count": len(all_recommendations),
            }
        }
        
        return synthesized_result

