import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from app.state.research_state import ResearchState
from app.agents.shared.llm import gemini_client

logger = logging.getLogger(__name__)

class ResearchPlan(BaseModel):
    market_overview_tasks: list[str] = Field(description="2 specific tasks for market analysis.")
    competitor_analysis_tasks: list[str] = Field(description="2 tasks for competitor analysis.")
    financial_analysis_tasks: list[str] = Field(description="2 tasks for financial metrics.")
    risk_analysis_tasks: list[str] = Field(description="2 tasks for risk identification.")

async def planner_node(state: ResearchState) -> Dict[str, Any]:
    """
    Analyzes the user query and generates a highly detailed research plan.
    Now supports up to 18 specific tasks thanks to API Key Rotation.
    """
    logger.info("--- GENERATING DEEP RESEARCH PLAN ---")
    query = state.get("query", "")
    sector = state.get("sector_classification", "Unknown")
    
    prompt = f"""Create a focused financial research plan for: "{query}" (sector: {sector}).
    Give 2 specific tasks per category: market overview, competitor analysis, financial metrics, risks."""
    
    try:
        plan_result = await gemini_client.ainvoke_structured(
            messages=[HumanMessage(content=prompt)],
            schema=ResearchPlan
        )
        
        formatted_plan = f"""### Research Plan\n- Market: {', '.join(plan_result.market_overview_tasks)}\n- Competitors: {', '.join(plan_result.competitor_analysis_tasks)}\n- Financials: {', '.join(plan_result.financial_analysis_tasks)}\n- Risks: {', '.join(plan_result.risk_analysis_tasks)}\n"""
        logger.info(f"Research plan generated successfully:\n{formatted_plan}")
        
        return {
            "research_plan": formatted_plan,
            "current_research_step": "planner_completed"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate research plan: {e}")
        return {
            "research_plan": "Failed to generate a detailed research plan.",
            "current_research_step": "planner_failed"
        }
