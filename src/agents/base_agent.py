"""
Base agent structure for worker agents.
Provides common functionality for all specialized agents.
"""

from typing import Dict, Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm() -> BaseChatModel:
    """
    Initialize and return the LLM (Google GenAI).
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=api_key,
    )


class BaseWorkerAgent:
    """
    Base class for worker agents.
    Provides common structure and methods.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        tools: list,
        llm: Optional[BaseChatModel] = None
    ):
        """
        Initialize base worker agent.
        
        Args:
            name: Agent name
            role: Agent role description
            system_prompt: System prompt defining agent behavior
            tools: List of tools available to the agent
            llm: Optional LLM instance (will create if not provided)
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tools = tools
        self.llm = llm or get_llm()
        
        # Bind tools to LLM
        self.agent = self.llm.bind_tools(tools)
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("{input}"),
        ])
    
    def analyze(self, molecule: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a molecule and return structured insights.
        
        Args:
            molecule: Name of the molecule to analyze
            context: Optional additional context
            
        Returns:
            Dictionary with structured insights
        """
        # This will be overridden by subclasses
        raise NotImplementedError("Subclasses must implement analyze method")
    
    def format_insights(self, raw_data: Dict[str, Any], analysis: str) -> Dict[str, Any]:
        """
        Format insights into structured output.
        
        Args:
            raw_data: Raw data from tool
            analysis: LLM analysis text
            
        Returns:
            Structured insights dictionary
        """
        return {
            "agent_name": self.name,
            "role": self.role,
            "molecule": raw_data.get("molecule", "Unknown"),
            "raw_data": raw_data,
            "analysis": analysis,
            "key_findings": self._extract_key_findings(raw_data),
            "recommendations": self._generate_recommendations(raw_data),
        }
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> list:
        """Extract key findings from data (to be overridden by subclasses)"""
        return []
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> list:
        """Generate recommendations from data (to be overridden by subclasses)"""
        return []

