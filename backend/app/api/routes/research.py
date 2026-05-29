import logging
from fastapi import APIRouter
from app.models.schemas import ResearchRequest
from app.graph.workflow import create_research_graph

router = APIRouter()
logger = logging.getLogger(__name__)

# Compile graph once
research_graph = create_research_graph()

@router.post("/")
async def trigger_research(request: ResearchRequest):
    query = request.query.strip()
    
    if not query or len(query) < 5:
        return {"status": "error", "error": "Please enter a valid query of at least 5 characters"}
        
    if len(query) > 500:
        query = query[:500]
        
    logger.info(f"Research request received: query='{query}' ticker='{request.company_symbol}'")
    try:
        logger.info("Invoking LangGraph Research Pipeline...")
        initial_state = {
            "query": query,
            "ticker": request.company_symbol or "NONE",
            "company_symbol": request.company_symbol or "",
            "search_history": [],
            "financial_data": {},
            "findings": []
        }
        
        # This is a blocking (async) call
        final_state = await research_graph.ainvoke(initial_state)
        
        return {
            "status": "success",
            "final_report": final_state.get("final_report", "Pipeline completed but no report was generated.")
        }
    except Exception as e:
        logger.error(f"Research pipeline failed: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}
