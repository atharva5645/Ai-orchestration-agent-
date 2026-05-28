import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

from app.state.research_state import ResearchState
from app.agents.shared.llm import gemini_client

logger = logging.getLogger(__name__)

class ReflectionOutput(BaseModel):
    missing_information: str = Field(description="Detailed analysis of what information is missing based on the research plan.")
    next_search_queries: List[str] = Field(description="1 to 3 highly specific search queries to find the missing information.")
    confidence_score: float = Field(description="Float from 0.0 to 1.0 indicating how complete the research is.")
    is_sufficient: bool = Field(description="True if you have gathered enough data to satisfy the entire research plan, False otherwise.")

async def reflection_node(state: ResearchState) -> Dict[str, Any]:
    """
    Acts as the 'Brain' of the system.
    Evaluates current findings against the research plan and decides the next moves.
    """
    logger.info("--- REFLECTION AGENT (EVALUATING FINDINGS) ---")
    query = state.get("query", "")
    research_plan = state.get("research_plan", "No plan provided.")
    findings = state.get("findings", [])
    
    findings_text = "\n\n".join(findings) if findings else "No findings gathered yet."
    
    sys_msg = SystemMessage(content="""You are an elite Autonomous Financial Reflection Agent.
Your job is to read the gathered findings and compare them strictly against the Research Plan.
If there are gaps, you must identify them and generate the exact search queries the Web Researcher should use next.
If the findings are comprehensive and cover the plan, set is_sufficient to True.""")

    prompt = f"""
    ORIGINAL USER QUERY: "{query}"
    
    RESEARCH PLAN TO EXECUTE:
    {research_plan}
    
    CURRENT FINDINGS GATHERED SO FAR:
    {findings_text}
    
    Perform adaptive reasoning. What financial gaps remain? What should be researched next?
    Generate up to 3 highly specific search queries to close the gaps.
    Determine your confidence score (0.0 to 1.0). If the research is fully complete, set is_sufficient to True.
    """
    
    try:
        logger.info("Calling Gemini for deep reflection...")
        reflection = await gemini_client.ainvoke_structured(
            messages=[sys_msg, HumanMessage(content=prompt)],
            schema=ReflectionOutput
        )
        
        logger.info(f"Missing Info: {reflection.missing_information}")
        logger.info(f"Next Queries: {reflection.next_search_queries}")
        logger.info(f"Confidence: {reflection.confidence_score} | Sufficient: {reflection.is_sufficient}")
        
        return {
            "reflection_output": reflection.missing_information,
            "next_search_queries": reflection.next_search_queries,
            "is_sufficient": reflection.is_sufficient,
            "current_research_step": "reflection_completed",
            "iteration_count": state.get("iteration_count", 0) + 1
        }
        
    except Exception as e:
        logger.error(f"Reflection failed: {e}")
        return {
            "reflection_output": "Failed to evaluate findings.",
            "next_search_queries": [],
            "is_sufficient": True, # Fail safe to avoid infinite loops
            "current_research_step": "reflection_failed",
            "iteration_count": state.get("iteration_count", 0) + 1
        }
