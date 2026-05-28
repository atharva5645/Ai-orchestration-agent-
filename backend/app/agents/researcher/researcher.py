import asyncio
import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage

from app.state.research_state import ResearchState
from app.tools.search.tavily_search import tavily_search_tool
from app.agents.shared.llm import gemini_client

logger = logging.getLogger(__name__)

async def researcher_node(state: ResearchState) -> Dict[str, Any]:
    """
    Acts as the 'Hands' of the system.
    Executes searches requested by the Reflection Agent and synthesizes the raw data.
    """
    query = state.get("query", "")
    iteration = state.get("iteration_count", 0) + 1
    next_queries = state.get("next_search_queries", [])
    
    logger.info(f"--- RESEARCHER NODE (Iteration {iteration}) ---")
    
    # Fallback if no queries were provided by reflection (e.g. first run)
    if not next_queries:
        logger.info("No specific queries provided. Using default query.")
        next_queries = [query]
        
    search_history = state.get("search_history", [])
    all_findings = state.get("findings", [])
    
    try:
        # Execute searches concurrently
        logger.info(f"Executing {len(next_queries)} searches via Tavily...")
        search_tasks = [tavily_search_tool.search(query=q, max_results=3) for q in next_queries]
        results_matrix = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        raw_text_for_synthesis = f"--- ITERATION {iteration} DATA ---\n"
        
        for idx, result_list in enumerate(results_matrix):
            if isinstance(result_list, Exception):
                logger.error(f"Search failed for '{next_queries[idx]}': {result_list}")
                continue
            
            for r in result_list:
                search_history.append({
                    "query": next_queries[idx],
                    "title": r.title,
                    "url": r.url
                })
                raw_text_for_synthesis += f"\nTitle: {r.title}\nSource: {r.url}\nContent: {r.content}\n"
        
        # Synthesize this iteration's data
        synthesis_prompt = f"""Extract key financial facts and figures from this data as concise bullet points. Skip ads/irrelevant content.

RAW DATA:
{raw_text_for_synthesis[:5000]}
"""
        
        logger.info("Synthesizing raw search data...")
        synthesis_response = await gemini_client.ainvoke([HumanMessage(content=synthesis_prompt)])
        synthesis_content = synthesis_response.content
        
        # Handle dicts/lists safely
        if isinstance(synthesis_content, list):
            synthesis_content = " ".join([str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in synthesis_content])
            
        logger.info(f"Synthesized Insights: {synthesis_content[:100]}...")
        all_findings.append(f"Iteration {iteration} Insights:\n" + str(synthesis_content))

        return {
            "search_history": search_history,
            "findings": all_findings,
            "iteration_count": iteration,
            "current_research_step": "research_executed"
        }
        
    except Exception as e:
        logger.error(f"Research execution failed: {e}")
        return {
            "search_history": search_history + [{"error": str(e)}],
            "iteration_count": iteration,
            "current_research_step": "research_failed"
        }
