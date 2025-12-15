"""
Web Intelligence Tool - Mock web search for guidelines, publications, and news.
Returns scientific and market intelligence from web sources.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
import random


def _get_mock_web_data(molecule: str, target_indication: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate realistic mock web intelligence data for a molecule.
    
    Args:
        molecule: Name of the molecule/drug
        target_indication: Optional target indication filter
        
    Returns:
        Dictionary with web intelligence data
    """
    # Mock sources
    source_types = [
        "Scientific Publication",
        "Clinical Guideline",
        "Regulatory News",
        "Market News",
        "Conference Abstract",
        "Review Article",
    ]
    
    # Mock journals/sources
    sources = [
        "Nature Medicine",
        "The Lancet",
        "New England Journal of Medicine",
        "FDA News Release",
        "EMA Press Release",
        "Pharma Industry News",
        "Clinical Guidelines Database",
        "PubMed",
    ]
    
    # Generate results
    num_results = random.randint(10, 25)
    results = []
    
    for i in range(num_results):
        source_type = random.choice(source_types)
        source = random.choice(sources)
        
        # Generate relevant snippets
        snippets = [
            f"{molecule} shows promise in {target_indication or 'new therapeutic areas'}",
            f"Recent study demonstrates efficacy of {molecule} in target population",
            f"Regulatory approval pathway for {molecule} repurposing appears feasible",
            f"Market analysis indicates growing demand for {molecule}-based therapies",
            f"Clinical evidence supports {molecule} use in expanded indications",
        ]
        
        results.append({
            "title": f"{molecule} {source_type}: {random.choice(['Analysis', 'Study', 'Update', 'Review'])}",
            "source": source,
            "source_type": source_type,
            "date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "url": f"https://example.com/{molecule.lower().replace(' ', '-')}-{i+1}",
            "snippet": random.choice(snippets),
            "relevance_score": round(random.uniform(0.5, 1.0), 2),
        })
    
    # Categorize by source type
    by_source_type = {}
    for result in results:
        st = result["source_type"]
        by_source_type[st] = by_source_type.get(st, []) + [result]
    
    # Key insights
    key_insights = [
        f"{num_results} relevant sources found",
        f"Top source type: {max(by_source_type.items(), key=lambda x: len(x[1]))[0] if by_source_type else 'N/A'}",
        f"Recent publications: {len([r for r in results if '2024' in r['date']])} in 2024",
        f"Evidence quality: {random.choice(['Strong', 'Moderate', 'Emerging'])}",
    ]
    
    return {
        "molecule": molecule,
        "target_indication": target_indication,
        "total_results": num_results,
        "results": sorted(results, key=lambda x: x["relevance_score"], reverse=True),
        "by_source_type": {k: len(v) for k, v in by_source_type.items()},
        "key_insights": key_insights,
        "data_source": "Web Intelligence Search (Mock)",
        "last_updated": "2024-Q4",
    }


@tool
def web_intelligence_tool(molecule: str, target_indication: Optional[str] = None) -> str:
    """
    Performs web search for guidelines, publications, and news about a molecule.
    
    This tool provides:
    - Scientific publications and research
    - Clinical guidelines
    - Regulatory news
    - Market intelligence
    - Evidence summaries
    
    Args:
        molecule: Name of the pharmaceutical molecule/drug to analyze
        target_indication: Optional target indication filter
        
    Returns:
        Formatted string with web intelligence insights
    """
    data = _get_mock_web_data(molecule, target_indication)
    
    # Format as readable string
    result = f"""
Web Intelligence Report for {data['molecule']}
{f"Target Indication: {data['target_indication']}" if data['target_indication'] else ""}
{'=' * 60}

Search Overview:
- Total Results: {data['total_results']}
- Source Types: {', '.join(data['by_source_type'].keys())}

Results by Source Type:
{chr(10).join(f'  • {source_type}: {count} results' for source_type, count in data['by_source_type'].items())}

Top Results:
{chr(10).join(f'  • [{r["source_type"]}] {r["title"]} ({r["source"]}, {r["date"]})' for r in data['results'][:8])}

Key Evidence Snippets:
{chr(10).join(f'  • {r["snippet"]}' for r in data['results'][:5])}

Key Insights:
{chr(10).join(f'  • {insight}' for insight in data['key_insights'])}

Data Source: {data['data_source']}
Last Updated: {data['last_updated']}
"""
    return result.strip()


def get_web_data_raw(molecule: str, target_indication: Optional[str] = None) -> Dict[str, Any]:
    """
    Get raw web intelligence data as dictionary (for programmatic use).
    
    Args:
        molecule: Name of the molecule
        target_indication: Optional target indication filter
        
    Returns:
        Dictionary with structured web intelligence data
    """
    return _get_mock_web_data(molecule, target_indication)

