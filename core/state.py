from typing import List, Dict, Any, TypedDict, Optional
from pydantic import BaseModel, Field

class ResearchState(TypedDict):
    """
    Comprehensive TypedDict State that tracks the graph history, steps, raw scraped data,
    source credibility metrics, and critic evaluation scores.
    """
    query: str
    raw_scraped_data: List[Dict[str, Any]]
    steps: List[str]
    history: List[Dict[str, str]]
    draft_report: str
    source_credibility: Dict[str, float]
    critic_scores: Dict[str, Any]
    next_node: str
    final_report: Optional[str]
