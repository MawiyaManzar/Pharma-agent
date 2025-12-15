"""
IQVIA Insights Tool - Mock market intelligence data source.
Returns market size, competition, growth data for pharmaceutical molecules.
"""

from typing import Dict, Any, Optional
from langchain_core.tools import tool
import random


def _get_mock_iqvia_data(molecule: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate realistic mock IQVIA market data for a molecule.
    
    Args:
        molecule: Name of the molecule/drug
        region: Optional region filter (e.g., "US", "EU", "Global")
        
    Returns:
        Dictionary with market intelligence data
    """
    # Mock data generation with realistic variations
    base_market_size = random.randint(500, 5000)  # in millions USD
    cagr = round(random.uniform(-5.0, 15.0), 2)
    competition_count = random.randint(3, 25)
    
    # Generate competitor names
    competitors = [
        f"{molecule} Generic A",
        f"{molecule} Generic B",
        f"{molecule} Brand X",
        f"{molecule} Brand Y",
        "Competitor Molecule 1",
        "Competitor Molecule 2",
    ][:competition_count]
    
    # Therapy areas
    therapy_areas = [
        "Cardiovascular",
        "Diabetes",
        "Oncology",
        "Neurology",
        "Infectious Diseases",
        "Respiratory",
    ]
    selected_therapy_areas = random.sample(therapy_areas, k=random.randint(1, 3))
    
    return {
        "molecule": molecule,
        "region": region or "Global",
        "market_size_usd_millions": base_market_size,
        "cagr_percent": cagr,
        "forecast_years": 5,
        "market_trend": "Growing" if cagr > 2 else "Stable" if cagr > -2 else "Declining",
        "competition": {
            "total_competitors": competition_count,
            "top_competitors": competitors[:5],
            "market_concentration": random.choice(["High", "Medium", "Low"]),
        },
        "therapy_areas": selected_therapy_areas,
        "key_insights": [
            f"Market size of ${base_market_size}M with {cagr}% CAGR",
            f"{competition_count} active competitors in the market",
            f"Primary therapy areas: {', '.join(selected_therapy_areas)}",
            f"Market concentration: {random.choice(['High', 'Medium', 'Low'])}",
        ],
        "data_source": "IQVIA Market Intelligence (Mock)",
        "last_updated": "2024-Q4",
    }


@tool
def iqvia_insights_tool(molecule: str, region: Optional[str] = None) -> str:
    """
    Fetches market intelligence data from IQVIA for a given molecule.
    
    This tool provides:
    - Market size and growth projections
    - Competitive landscape analysis
    - Therapy area insights
    - Market trends and forecasts
    
    Args:
        molecule: Name of the pharmaceutical molecule/drug to analyze
        region: Optional region filter (e.g., "US", "EU", "Global"). Defaults to "Global"
        
    Returns:
        Formatted string with market intelligence insights
    """
    data = _get_mock_iqvia_data(molecule, region)
    
    # Format as readable string
    result = f"""
IQVIA Market Intelligence Report for {data['molecule']}
Region: {data['region']}
{'=' * 60}

Market Overview:
- Market Size: ${data['market_size_usd_millions']:,}M USD
- CAGR (5-year): {data['cagr_percent']}%
- Market Trend: {data['market_trend']}

Competitive Landscape:
- Total Competitors: {data['competition']['total_competitors']}
- Market Concentration: {data['competition']['market_concentration']}
- Top Competitors: {', '.join(data['competition']['top_competitors'][:3])}

Therapy Areas: {', '.join(data['therapy_areas'])}

Key Insights:
{chr(10).join(f'  • {insight}' for insight in data['key_insights'])}

Data Source: {data['data_source']}
Last Updated: {data['last_updated']}
"""
    return result.strip()


def get_iqvia_data_raw(molecule: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Get raw IQVIA data as dictionary (for programmatic use).
    
    Args:
        molecule: Name of the molecule
        region: Optional region filter
        
    Returns:
        Dictionary with structured market data
    """
    return _get_mock_iqvia_data(molecule, region)

