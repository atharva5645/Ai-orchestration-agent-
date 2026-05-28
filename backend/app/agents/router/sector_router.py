from typing import Literal
from pydantic import BaseModel, Field
from app.state.research_state import ResearchState
from app.agents.shared.llm import gemini_client
import logging

logger = logging.getLogger(__name__)

class SectorClassification(BaseModel):
    is_finance_query: bool = Field(description="True if the query is related to financial analysis, stocks, or companies. False otherwise.")
    sector: str = Field(description="The industry sector (e.g., 'IT', 'Pharma', 'Banking', 'Unknown', 'Rejected')")
    confidence_score: float = Field(description="Confidence score from 0.0 to 1.0")
    research_complexity: str = Field(description="Estimated complexity: 'Low', 'Medium', 'High'")
    reasoning: str = Field(description="Brief reasoning for the classification")

async def router_node(state: ResearchState):
    """
    Analyzes the user query and routes to the appropriate sector pipeline or rejects it.
    """
    logger.info("--- ROUTING QUERY ---")
    query = state.get("query", "")
    
    prompt = f"""
    Analyze the following user query: "{query}"
    
    Classify the query to determine if it is a financial research request.
    If it is NOT about finance, companies, or markets (e.g. asking for a recipe, coding help, or general chatter), set is_finance_query to False and sector to 'Rejected'.
    If it is a financial query, classify the sector (e.g., 'IT', 'Pharma', etc.) and estimate the complexity of the research required.
    """
    
    from langchain_core.messages import HumanMessage
    try:
        result = await gemini_client.ainvoke_structured(
            messages=[HumanMessage(content=prompt)],
            schema=SectorClassification
        )
        
        sector = result.sector if result.is_finance_query else "Rejected"
        logger.info(f"Router Classification: {sector} (Confidence: {result.confidence_score})")
        
        final_report = ""
        if sector == "Rejected":
            final_report = "I apologize, but we only provide answers to questions regarding finance."
        else:
            final_report = ""

        return {
            "sector_classification": sector,
            "current_research_step": "router_completed",
            "final_report": final_report
        }
    except Exception as e:
        logger.error(f"Router failed to classify: {e}")
        # Fallback logic
        return {
            "sector_classification": "Unknown",
            "current_research_step": "router_completed",
            "final_report": ""
        }
