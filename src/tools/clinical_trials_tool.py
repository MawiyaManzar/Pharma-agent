"""
Clinical Trials Tool - Mock ClinicalTrials.gov/WHO ICTRP API.
Returns ongoing and completed trial data for molecules.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
import random
from datetime import datetime, timedelta


def _get_mock_clinical_trials_data(molecule: str, mechanism: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate realistic mock clinical trial data for a molecule.
    
    Args:
        molecule: Name of the molecule/drug
        mechanism: Optional mechanism of action filter
        
    Returns:
        Dictionary with clinical trial data
    """
    # Generate random number of trials
    num_trials = random.randint(8, 30)
    
    # Mock sponsors
    sponsors = [
        "National Institutes of Health",
        "PharmaCorp Inc.",
        "University Medical Center",
        "BioTech Solutions",
        "Global Research Foundation",
        "Clinical Research Organization",
    ]
    
    # Trial phases
    phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Not Applicable"]
    
    # Indications
    indications = [
        "Type 2 Diabetes",
        "Cardiovascular Disease",
        "Cancer",
        "Alzheimer's Disease",
        "Rheumatoid Arthritis",
        "Hypertension",
        "Obesity",
        "Chronic Pain",
    ]
    
    # Generate trial list
    trials = []
    for i in range(num_trials):
        # Random dates
        start_days_ago = random.randint(0, 2000)
        start_date = datetime.now() - timedelta(days=start_days_ago)
        duration_days = random.randint(30, 1800)
        end_date = start_date + timedelta(days=duration_days)
        
        status = random.choice([
            "Recruiting",
            "Active, not recruiting",
            "Completed",
            "Terminated",
            "Suspended",
        ])
        
        phase = random.choice(phases)
        indication = random.choice(indications)
        
        # Geography
        countries = random.sample(
            ["USA", "UK", "Canada", "Germany", "France", "India", "China", "Brazil"],
            k=random.randint(1, 4)
        )
        
        trials.append({
            "trial_id": f"NCT{random.randint(10000000, 99999999)}",
            "title": f"Study of {molecule} in {indication}",
            "sponsor": random.choice(sponsors),
            "phase": phase,
            "status": status,
            "indication": indication,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d") if end_date < datetime.now() else "Ongoing",
            "countries": countries,
            "participants": random.randint(20, 5000),
        })
    
    # Categorize trials
    ongoing_trials = [t for t in trials if t["status"] in ["Recruiting", "Active, not recruiting"]]
    completed_trials = [t for t in trials if t["status"] == "Completed"]
    terminated_trials = [t for t in trials if t["status"] in ["Terminated", "Suspended"]]
    
    # Phase distribution
    phase_dist = {}
    for phase in phases:
        count = len([t for t in trials if t["phase"] == phase])
        if count > 0:
            phase_dist[phase] = count
    
    # Emerging indications (trials in Phase 2 or 3)
    emerging_indications = {}
    for trial in trials:
        if trial["phase"] in ["Phase 2", "Phase 3"] and trial["status"] in ["Recruiting", "Active, not recruiting"]:
            ind = trial["indication"]
            emerging_indications[ind] = emerging_indications.get(ind, 0) + 1
    
    return {
        "molecule": molecule,
        "mechanism": mechanism,
        "total_trials": num_trials,
        "ongoing_trials": len(ongoing_trials),
        "completed_trials": len(completed_trials),
        "terminated_trials": len(terminated_trials),
        "trials": trials,
        "phase_distribution": phase_dist,
        "emerging_indications": dict(sorted(emerging_indications.items(), key=lambda x: x[1], reverse=True)),
        "key_insights": [
            f"{len(ongoing_trials)} ongoing trials, {len(completed_trials)} completed",
            f"Phase distribution: {', '.join(f'{k}: {v}' for k, v in phase_dist.items())}",
            f"Top emerging indication: {max(emerging_indications.items(), key=lambda x: x[1])[0] if emerging_indications else 'None identified'}" if emerging_indications else "No emerging indications identified",
            f"Geographic spread: {len(set(country for t in trials for country in t['countries']))} countries",
        ],
        "data_source": "ClinicalTrials.gov / WHO ICTRP (Mock)",
        "last_updated": "2024-Q4",
    }


@tool
def clinical_trials_tool(molecule: str, mechanism: Optional[str] = None) -> str:
    """
    Retrieves clinical trial data for a given molecule.
    
    This tool provides:
    - Ongoing and completed trials
    - Phase distribution
    - Emerging indications
    - Geographic distribution
    - Trial status and timelines
    
    Args:
        molecule: Name of the pharmaceutical molecule/drug to analyze
        mechanism: Optional mechanism of action filter
        
    Returns:
        Formatted string with clinical trial insights
    """
    data = _get_mock_clinical_trials_data(molecule, mechanism)
    
    # Format as readable string
    result = f"""
Clinical Trials Report for {data['molecule']}
{f"Mechanism: {data['mechanism']}" if data['mechanism'] else ""}
{'=' * 60}

Trial Overview:
- Total Trials: {data['total_trials']}
- Ongoing: {data['ongoing_trials']}
- Completed: {data['completed_trials']}
- Terminated/Suspended: {data['terminated_trials']}

Phase Distribution:
{chr(10).join(f'  • {phase}: {count} trials' for phase, count in data['phase_distribution'].items())}

Emerging Indications (Phase 2/3 Active):
{chr(10).join(f'  • {indication}: {count} trials' for indication, count in list(data['emerging_indications'].items())[:5]) if data['emerging_indications'] else '  • No emerging indications identified'}

Sample Ongoing Trials:
{chr(10).join(f'  • {t["trial_id"]}: {t["title"]} ({t["phase"]}, {t["status"]})' for t in data['trials'] if t["status"] in ["Recruiting", "Active, not recruiting"])[:5]}

Key Insights:
{chr(10).join(f'  • {insight}' for insight in data['key_insights'])}

Data Source: {data['data_source']}
Last Updated: {data['last_updated']}
"""
    return result.strip()


def get_clinical_trials_data_raw(molecule: str, mechanism: Optional[str] = None) -> Dict[str, Any]:
    """
    Get raw clinical trials data as dictionary (for programmatic use).
    
    Args:
        molecule: Name of the molecule
        mechanism: Optional mechanism of action filter
        
    Returns:
        Dictionary with structured trial data
    """
    return _get_mock_clinical_trials_data(molecule, mechanism)

