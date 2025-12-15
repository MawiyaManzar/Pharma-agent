"""
Internal Insights Tool - Mock internal document repository access.
Returns strategy decks, internal documents, and field insights.
"""

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
import random


def _get_mock_internal_data(molecule: str, document_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate realistic mock internal document data for a molecule.
    
    Args:
        molecule: Name of the molecule/drug
        document_filter: Optional document type filter
        
    Returns:
        Dictionary with internal insights data
    """
    # Mock document types
    document_types = [
        "Strategy Deck",
        "Market Research Report",
        "Field Intelligence",
        "Competitive Analysis",
        "Regulatory Brief",
        "Portfolio Review",
    ]
    
    # Mock departments
    departments = [
        "Business Development",
        "Market Intelligence",
        "Regulatory Affairs",
        "R&D Strategy",
        "Commercial Planning",
    ]
    
    # Generate document list
    num_docs = random.randint(3, 12)
    documents = []
    
    for i in range(num_docs):
        doc_type = random.choice(document_types)
        department = random.choice(departments)
        
        # Generate key takeaways
        takeaways = [
            f"{molecule} identified as priority molecule for repurposing",
            f"Market opportunity in {random.choice(['diabetes', 'cardiovascular', 'oncology'])} segment",
            f"Internal strategy alignment: {random.choice(['High', 'Medium', 'Low'])}",
            f"Regulatory pathway: {random.choice(['505(b)(2)', 'ANDA', 'NDA'])}",
            f"Competitive threat level: {random.choice(['High', 'Medium', 'Low'])}",
        ]
        
        documents.append({
            "document_id": f"INT-{random.randint(1000, 9999)}",
            "title": f"{doc_type}: {molecule} Analysis",
            "type": doc_type,
            "department": department,
            "date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "key_takeaways": random.sample(takeaways, k=random.randint(2, 4)),
            "relevance_score": round(random.uniform(0.6, 1.0), 2),
        })
    
    # Strategy alignment
    strategy_alignment = random.choice(["High", "Medium", "Low"])
    
    # Internal priorities
    priorities = [
        "Top Priority - Active Development",
        "Medium Priority - Under Evaluation",
        "Low Priority - On Hold",
        "Strategic Interest - Monitoring",
    ]
    priority_level = random.choice(priorities)
    
    # Field insights
    field_insights = [
        f"Field team reports strong physician interest in {molecule} for new indications",
        f"Market research indicates unmet need in target patient population",
        f"Competitive intelligence suggests limited market entry barriers",
        f"Regulatory team confirms feasible pathway for repurposing",
    ]
    
    # Key insights summary
    key_insights = [
        f"Strategy alignment: {strategy_alignment}",
        f"Priority level: {priority_level}",
        f"{num_docs} relevant internal documents found",
        f"Top department: {max(set(d['department'] for d in documents), key=documents.count)}",
    ]
    
    return {
        "molecule": molecule,
        "document_filter": document_filter,
        "total_documents": num_docs,
        "documents": documents,
        "strategy_alignment": strategy_alignment,
        "priority_level": priority_level,
        "field_insights": random.sample(field_insights, k=random.randint(2, 4)),
        "key_insights": key_insights,
        "data_source": "Internal Document Repository (Mock)",
        "last_updated": "2024-Q4",
    }


@tool
def internal_insights_tool(molecule: str, document_filter: Optional[str] = None) -> str:
    """
    Retrieves internal documents and insights for a given molecule.
    
    This tool provides:
    - Strategy decks and market research
    - Field intelligence
    - Internal priorities and alignment
    - Department-specific insights
    
    Args:
        molecule: Name of the pharmaceutical molecule/drug to analyze
        document_filter: Optional document type filter (e.g., "Strategy Deck", "Market Research")
        
    Returns:
        Formatted string with internal insights
    """
    data = _get_mock_internal_data(molecule, document_filter)
    
    # Format as readable string
    result = f"""
Internal Insights Report for {data['molecule']}
{f"Document Filter: {data['document_filter']}" if data['document_filter'] else ""}
{'=' * 60}

Document Overview:
- Total Documents: {data['total_documents']}
- Strategy Alignment: {data['strategy_alignment']}
- Priority Level: {data['priority_level']}

Key Documents:
{chr(10).join(f'  • {doc["document_id"]}: {doc["title"]} ({doc["department"]}, {doc["date"]})' for doc in sorted(data['documents'], key=lambda x: x['relevance_score'], reverse=True)[:5])}

Field Insights:
{chr(10).join(f'  • {insight}' for insight in data['field_insights'])}

Key Takeaways from Documents:
{chr(10).join(f'  • {takeaway}' for doc in data['documents'][:3] for takeaway in doc['key_takeaways'][:2])}

Key Insights:
{chr(10).join(f'  • {insight}' for insight in data['key_insights'])}

Data Source: {data['data_source']}
Last Updated: {data['last_updated']}
"""
    return result.strip()


def get_internal_data_raw(molecule: str, document_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Get raw internal insights data as dictionary (for programmatic use).
    
    Args:
        molecule: Name of the molecule
        document_filter: Optional document type filter
        
    Returns:
        Dictionary with structured internal insights data
    """
    return _get_mock_internal_data(molecule, document_filter)

