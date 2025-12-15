"""
Patent Landscape Tool - Mock USPTO-like patent search and FTO analysis.
Returns patent data and Freedom-To-Operate assessment.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
import random
from datetime import datetime, timedelta


def _get_mock_patent_data(molecule: str, therapy_area: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate realistic mock patent data for a molecule.
    
    Args:
        molecule: Name of the molecule/drug
        therapy_area: Optional therapy area filter
        
    Returns:
        Dictionary with patent landscape data
    """
    # Generate random number of patents
    num_patents = random.randint(5, 20)
    
    # Mock assignees
    assignees = [
        "PharmaCorp Inc.",
        "BioTech Solutions Ltd.",
        "Global Pharma Co.",
        "Innovation Labs",
        "Research Institute",
        "Generic Pharma LLC",
    ]
    
    # Generate patent list
    patents = []
    for i in range(num_patents):
        # Random expiry date (some expired, some active)
        years_ago = random.randint(0, 25)
        filing_date = datetime.now() - timedelta(days=years_ago * 365)
        expiry_date = filing_date + timedelta(days=20 * 365)  # 20-year term
        
        patent_type = random.choice([
            "Composition of Matter",
            "Method of Use",
            "Formulation",
            "Process",
            "Dosage Form",
        ])
        
        patents.append({
            "patent_number": f"US{random.randint(10000000, 99999999)}",
            "title": f"{molecule} {patent_type} Patent",
            "assignee": random.choice(assignees),
            "filing_date": filing_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "status": "Active" if expiry_date > datetime.now() else "Expired",
            "type": patent_type,
            "jurisdiction": random.choice(["US", "EP", "WO", "IN"]),
        })
    
    # Separate active and expired
    active_patents = [p for p in patents if p["status"] == "Active"]
    expired_patents = [p for p in patents if p["status"] == "Expired"]
    
    # FTO Assessment
    if len(active_patents) == 0:
        fto_status = "Green"
        fto_risk = "Low"
        fto_reason = "No active patents blocking the molecule"
    elif len(active_patents) <= 3:
        fto_status = "Amber"
        fto_risk = "Medium"
        fto_reason = f"{len(active_patents)} active patents may require licensing or design-around"
    else:
        fto_status = "Red"
        fto_risk = "High"
        fto_reason = f"{len(active_patents)} active patents create significant FTO risk"
    
    # Key blocking patents
    blocking_patents = active_patents[:3] if active_patents else []
    
    # Expiry timeline
    upcoming_expiries = [
        p for p in active_patents
        if datetime.strptime(p["expiry_date"], "%Y-%m-%d") < datetime.now() + timedelta(days=5*365)
    ]
    
    return {
        "molecule": molecule,
        "therapy_area": therapy_area,
        "total_patents": num_patents,
        "active_patents": len(active_patents),
        "expired_patents": len(expired_patents),
        "patents": patents,
        "fto_assessment": {
            "status": fto_status,
            "risk_level": fto_risk,
            "reason": fto_reason,
            "blocking_patents": blocking_patents,
        },
        "upcoming_expiries": len(upcoming_expiries),
        "key_insights": [
            f"FTO Status: {fto_status} ({fto_risk} risk)",
            f"{len(active_patents)} active patents, {len(expired_patents)} expired",
            f"{len(upcoming_expiries)} patents expiring in next 5 years",
            f"Top assignee: {max(set(p['assignee'] for p in patents), key=patents.count)}" if patents else "No patents found",
        ],
        "data_source": "USPTO Patent Database (Mock)",
        "last_updated": "2024-Q4",
    }


@tool
def patent_landscape_tool(molecule: str, therapy_area: Optional[str] = None) -> str:
    """
    Searches patent database for a given molecule and performs FTO analysis.
    
    This tool provides:
    - Patent landscape overview
    - Active vs expired patents
    - Freedom-To-Operate (FTO) assessment
    - Key blocking patents
    - Expiry timeline
    
    Args:
        molecule: Name of the pharmaceutical molecule/drug to analyze
        therapy_area: Optional therapy area filter (e.g., "Cardiovascular", "Oncology")
        
    Returns:
        Formatted string with patent landscape and FTO insights
    """
    data = _get_mock_patent_data(molecule, therapy_area)
    
    # Format as readable string
    result = f"""
Patent Landscape Report for {data['molecule']}
{f"Therapy Area: {data['therapy_area']}" if data['therapy_area'] else ""}
{'=' * 60}

Patent Overview:
- Total Patents Found: {data['total_patents']}
- Active Patents: {data['active_patents']}
- Expired Patents: {data['expired_patents']}
- Upcoming Expiries (5 years): {data['upcoming_expiries']}

FTO Assessment:
- Status: {data['fto_assessment']['status']} ({data['fto_assessment']['risk_level']} Risk)
- Assessment: {data['fto_assessment']['reason']}

Key Blocking Patents:
{chr(10).join(f'  • {p["patent_number"]} - {p["title"]} ({p["assignee"]}, expires {p["expiry_date"]})' for p in data['fto_assessment']['blocking_patents'][:3]) if data['fto_assessment']['blocking_patents'] else '  • No blocking patents identified'}

Sample Patents:
{chr(10).join(f'  • {p["patent_number"]}: {p["title"]} - {p["status"]} (expires {p["expiry_date"]})' for p in data['patents'][:5])}

Key Insights:
{chr(10).join(f'  • {insight}' for insight in data['key_insights'])}

Data Source: {data['data_source']}
Last Updated: {data['last_updated']}
"""
    return result.strip()


def get_patent_data_raw(molecule: str, therapy_area: Optional[str] = None) -> Dict[str, Any]:
    """
    Get raw patent data as dictionary (for programmatic use).
    
    Args:
        molecule: Name of the molecule
        therapy_area: Optional therapy area filter
        
    Returns:
        Dictionary with structured patent data
    """
    return _get_mock_patent_data(molecule, therapy_area)

