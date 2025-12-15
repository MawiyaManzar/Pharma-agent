"""Worker agents for specialized analysis"""

from .base_agent import BaseWorkerAgent, get_llm
from .iqvia_agent import IQVIAInsightsAgent
from .exim_agent import EXIMTradeAgent
from .patent_agent import PatentLandscapeAgent
from .clinical_trials_agent import ClinicalTrialsAgent
from .internal_insights_agent import InternalInsightsAgent
from .web_intelligence_agent import WebIntelligenceAgent

__all__ = [
    "BaseWorkerAgent",
    "get_llm",
    "IQVIAInsightsAgent",
    "EXIMTradeAgent",
    "PatentLandscapeAgent",
    "ClinicalTrialsAgent",
    "InternalInsightsAgent",
    "WebIntelligenceAgent",
]

# List of all worker agents
ALL_WORKER_AGENTS = [
    IQVIAInsightsAgent,
    EXIMTradeAgent,
    PatentLandscapeAgent,
    ClinicalTrialsAgent,
    InternalInsightsAgent,
    WebIntelligenceAgent,
]
