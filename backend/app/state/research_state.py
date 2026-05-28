import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class ResearchState(TypedDict):
    """
    LangGraph-compatible state for the Financial Deep Research Agent.
    Tracks all necessary context for multi-agent, iterative research workflows.
    """
    
    # Standard LangGraph message passing
    messages: Annotated[List[BaseMessage], operator.add]
    
    # User Inputs & Planning
    query: str
    research_plan: str
    sector_classification: str
    
    # Iterative Research Data
    search_history: Annotated[List[Dict[str, Any]], operator.add]
    findings: Annotated[List[str], operator.add]
    reflection_output: str
    next_search_queries: List[str]
    is_sufficient: bool
    current_research_step: str
    iteration_count: int
    
    # Specialized Data
    financial_data: Dict[str, Any]
    retrieved_documents: Annotated[List[str], operator.add] # For future RAG support
    
    # Output
    final_report: str
