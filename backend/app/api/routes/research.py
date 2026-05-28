import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import ResearchRequest, ResearchResponse
from app.services.fast_research import run_fast_research

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ResearchResponse)
async def trigger_research(request: ResearchRequest):
    logger.info(f"Research request received: query='{request.query}' ticker='{request.company_symbol}'")
    try:
        logger.info("Invoking Fast Research Pipeline...")
        report = await run_fast_research(request.query, request.company_symbol or "")
        
        if not report:
            report = "The fast research pipeline completed but did not produce a report."

        return ResearchResponse(
            status="completed",
            final_report=report
        )
    except Exception as e:
        logger.error(f"Research pipeline failed: {e}", exc_info=True)
        # Return the error as a visible report instead of crashing the frontend
        return ResearchResponse(
            status="error",
            final_report=None,
            error=str(e)
        )
