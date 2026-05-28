import asyncio
import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from app.agents.shared.llm import gemini_client
from app.tools.search.tavily_search import tavily_search_tool
from app.tools.finance.market_data import get_company_info

logger = logging.getLogger(__name__)

class BrainstormResult(BaseModel):
    ticker: str = Field(description="The exact stock ticker symbol if applicable, otherwise 'NONE'")
    search_queries: list[str] = Field(description="Exactly 4 specific web search queries to research this topic.")

async def run_fast_research(query: str, ticker: str = "") -> str:
    """Executes the 2-Call Fast Research Pipeline."""
    
    # LLM Call 1: Brainstorming
    logger.info("Executing Fast Research - Call 1 (Brainstorming)")
    prompt1 = f"""
    You are an expert financial analyst. 
    The user asked: "{query}"
    The provided ticker is: "{ticker}"

    Determine the most accurate stock ticker for this query (return "NONE" if not applicable).
    Then, write exactly 4 highly specific Google Search queries to gather the necessary data.
    """
    
    try:
        brainstorm = await gemini_client.ainvoke_structured(
            messages=[HumanMessage(content=prompt1)],
            schema=BrainstormResult
        )
    except Exception as e:
        logger.error(f"Brainstorming failed: {e}")
        return f"Research failed during brainstorming: {str(e)}"
    
    queries = brainstorm.search_queries[:4]
    final_ticker = brainstorm.ticker if brainstorm.ticker != "NONE" else ticker
    
    # Step 2: Python Data Scraper (0 LLM Calls)
    logger.info(f"Executing 4 concurrent searches + YFinance for ticker '{final_ticker}'")
    
    search_tasks = [tavily_search_tool.search(query=q, max_results=3) for q in queries]
    results_matrix = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    raw_data = "--- WEB SEARCH RESULTS ---\n"
    for idx, result_list in enumerate(results_matrix):
        if isinstance(result_list, Exception):
            continue
        for r in result_list:
            raw_data += f"Source: {r.url}\nContent: {r.content[:1500]}\n\n"
            
    if final_ticker and final_ticker != "NONE":
        # Run YFinance sync function in executor or just call it directly since it's requests-based
        info = get_company_info(final_ticker)
        raw_data += f"--- YAHOO FINANCE DATA FOR {final_ticker} ---\n"
        raw_data += str(info) + "\n\n"
        
    # Limit raw data size to save input tokens
    raw_data = raw_data[:20000]
    
    # LLM Call 2: Master Analyst
    logger.info("Executing Fast Research - Call 2 (Master Analyst)")
    prompt2 = f"""
    You are a Wall Street Master Analyst. Write a comprehensive, final financial report based ONLY on the following data.
    Organize the report with clear headings, bullet points, and actionable insights. Do not hallucinate.
    
    USER QUERY: {query}
    
    RAW DATA:
    {raw_data}
    """
    
    try:
        report_response = await gemini_client.ainvoke([HumanMessage(content=prompt2)])
        return str(report_response.content)
    except Exception as e:
        logger.error(f"Master Analyst failed: {e}")
        return f"Research failed during final report generation: {str(e)}"
