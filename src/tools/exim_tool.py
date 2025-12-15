"""
EXIM Trade Tool - Mock import/export and formulation movement data.
Returns trade intelligence for pharmaceutical molecules.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
import random


def _get_mock_exim_data(molecule: str) -> Dict[str, Any]:
    """
    Generate realistic mock EXIM trade data for a molecule.
    
    Args:
        molecule: Name of the molecule/drug
        
    Returns:
        Dictionary with trade intelligence data
    """
    # Mock countries and their trade roles
    exporter_countries = ["China", "India", "Germany", "Italy", "Spain"]
    importer_countries = ["USA", "UK", "Canada", "Australia", "Japan"]
    
    # Generate import/export data
    top_exporters = random.sample(exporter_countries, k=random.randint(2, 4))
    top_importers = random.sample(importer_countries, k=random.randint(2, 4))
    
    # Generate formulation types
    formulations = [
        "Tablet",
        "Capsule",
        "Injectable",
        "Oral Solution",
        "Topical Cream",
    ]
    selected_formulations = random.sample(formulations, k=random.randint(2, 4))
    
    # Calculate import dependency
    import_dependency_percent = round(random.uniform(30, 90), 1)
    
    # Risk assessment
    if import_dependency_percent > 70:
        risk_level = "High"
        risk_zones = top_exporters[:2]
    elif import_dependency_percent > 50:
        risk_level = "Medium"
        risk_zones = top_exporters[:1]
    else:
        risk_level = "Low"
        risk_zones = []
    
    # Trade volume in metric tons
    total_import_volume = round(random.uniform(100, 5000), 2)
    total_export_volume = round(random.uniform(50, 3000), 2)
    
    return {
        "molecule": molecule,
        "import_dependency_percent": import_dependency_percent,
        "risk_level": risk_level,
        "risk_zones": risk_zones,
        "top_exporters": [
            {"country": country, "volume_tons": round(random.uniform(50, 2000), 2)}
            for country in top_exporters
        ],
        "top_importers": [
            {"country": country, "volume_tons": round(random.uniform(100, 3000), 2)}
            for country in top_importers
        ],
        "formulations": selected_formulations,
        "total_import_volume_tons": total_import_volume,
        "total_export_volume_tons": total_export_volume,
        "trade_trend": random.choice(["Increasing", "Stable", "Declining"]),
        "key_insights": [
            f"Import dependency: {import_dependency_percent}%",
            f"Risk level: {risk_level}",
            f"Top exporter: {top_exporters[0]}" if top_exporters else "No major exporters",
            f"Primary formulations: {', '.join(selected_formulations[:2])}",
        ],
        "data_source": "EXIM Trade Intelligence (Mock)",
        "last_updated": "2024-Q4",
    }


@tool
def exim_trade_tool(molecule: str) -> str:
    """
    Fetches import/export trade data for a given molecule.
    
    This tool provides:
    - Import dependency analysis
    - Top exporter and importer countries
    - Formulation movement data
    - Supply chain risk assessment
    
    Args:
        molecule: Name of the pharmaceutical molecule/drug to analyze
        
    Returns:
        Formatted string with trade intelligence insights
    """
    data = _get_mock_exim_data(molecule)
    
    # Format as readable string
    result = f"""
EXIM Trade Intelligence Report for {data['molecule']}
{'=' * 60}

Import/Export Overview:
- Import Dependency: {data['import_dependency_percent']}%
- Risk Level: {data['risk_level']}
- Total Import Volume: {data['total_import_volume_tons']} metric tons
- Total Export Volume: {data['total_export_volume_tons']} metric tons
- Trade Trend: {data['trade_trend']}

Top Exporters:
{chr(10).join(f'  • {exp["country"]}: {exp["volume_tons"]} tons' for exp in data['top_exporters'][:3])}

Top Importers:
{chr(10).join(f'  • {imp["country"]}: {imp["volume_tons"]} tons' for imp in data['top_importers'][:3])}

Formulations in Trade: {', '.join(data['formulations'])}

Risk Assessment:
- Risk Level: {data['risk_level']}
{f'  • Risk Zones: {", ".join(data["risk_zones"])}' if data['risk_zones'] else '  • No significant risk zones identified'}

Key Insights:
{chr(10).join(f'  • {insight}' for insight in data['key_insights'])}

Data Source: {data['data_source']}
Last Updated: {data['last_updated']}
"""
    return result.strip()


def get_exim_data_raw(molecule: str) -> Dict[str, Any]:
    """
    Get raw EXIM data as dictionary (for programmatic use).
    
    Args:
        molecule: Name of the molecule
        
    Returns:
        Dictionary with structured trade data
    """
    return _get_mock_exim_data(molecule)

