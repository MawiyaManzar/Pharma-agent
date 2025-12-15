"""Tools and data source integrations"""

from .iqvia_tool import iqvia_insights_tool, get_iqvia_data_raw
from .exim_tool import exim_trade_tool, get_exim_data_raw
from .patent_tool import patent_landscape_tool, get_patent_data_raw
from .clinical_trials_tool import clinical_trials_tool, get_clinical_trials_data_raw
from .internal_insights_tool import internal_insights_tool, get_internal_data_raw
from .web_intelligence_tool import web_intelligence_tool, get_web_data_raw

__all__ = [
    # IQVIA Tool
    "iqvia_insights_tool",
    "get_iqvia_data_raw",
    # EXIM Tool
    "exim_trade_tool",
    "get_exim_data_raw",
    # Patent Tool
    "patent_landscape_tool",
    "get_patent_data_raw",
    # Clinical Trials Tool
    "clinical_trials_tool",
    "get_clinical_trials_data_raw",
    # Internal Insights Tool
    "internal_insights_tool",
    "get_internal_data_raw",
    # Web Intelligence Tool
    "web_intelligence_tool",
    "get_web_data_raw",
]

# List of all LangChain tools for easy access
ALL_TOOLS = [
    iqvia_insights_tool,
    exim_trade_tool,
    patent_landscape_tool,
    clinical_trials_tool,
    internal_insights_tool,
    web_intelligence_tool,
]
