import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from app.state.research_state import ResearchState
from app.agents.shared.llm import gemini_client

logger = logging.getLogger(__name__)

class RouterPlannerOutput(BaseModel):
    is_finance_query: bool
    sector: str
    ticker: str
    search_queries: list[str]

async def router_planner_node(state: ResearchState) -> Dict[str, Any]:
    """
    Combined Router and Planner node.
    Checks if the query is finance-related, extracts ticker, and generates exactly 4 search queries.
    """
    query = state.get("query", "")
    logger.info("--- ROUTER & PLANNER NODE ---")
    
    prompt = f"""
You are a financial research assistant.
Analyze this query: "{query}"

Step 1 - Is this finance-related? (stocks, companies, markets, investments, sectors)
If NOT finance, set is_finance_query=False, sector="Rejected", ticker="NONE", search_queries=[].

Step 2 - If finance query:
- Classify the sector (IT, Banking, Pharma, FMCG, Auto, Energy, etc.)
- Extract the stock ticker if a specific company is mentioned
  For Indian companies append .NS (e.g. INFY.NS, HDFCBANK.NS, RELIANCE.NS)
  For US companies use standard ticker (e.g. AAPL, TSLA, MSFT)
  If no specific company, return "NONE"
- Write exactly 4 highly specific search queries to research this topic

Return structured output only.
"""
    
    logger.info("Analyzing query routing & planning via Gemini...")
    try:
        result = await gemini_client.ainvoke_structured(
            messages=[HumanMessage(content=prompt)],
            schema=RouterPlannerOutput
        )
        
        is_finance = result.is_finance_query
        sector = result.sector
        ticker = result.ticker
        queries = result.search_queries
        
        logger.info(f"Is Finance: {is_finance}, Sector: {sector}, Ticker: {ticker}")
        logger.info(f"Generated queries: {queries}")
        
        if not is_finance:
            return {
                "sector_classification": "Rejected",
                "extracted_ticker": "NONE",
                "next_search_queries": [],
                "final_report": "I apologize, but I only answer finance-related questions.",
                "current_research_step": "router_completed"
            }
        else:
            return {
                "sector_classification": sector,
                "extracted_ticker": ticker,
                "next_search_queries": queries,
                "current_research_step": "planner_completed"
            }
            
    except Exception as e:
        logger.error(f"Router/Planner failed: {e}")
        return {
            "sector_classification": "Rejected",
            "extracted_ticker": "NONE",
            "next_search_queries": [],
            "final_report": f"Failed to analyze query due to backend error: {str(e)}\n\nThis usually means your Gemini API keys are exhausted. Please wait for the quota to reset.",
            "current_research_step": "router_failed"
        }
