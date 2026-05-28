from app.state.research_state import ResearchState
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.shared.llm import gemini_client
import logging
import json

logger = logging.getLogger(__name__)

async def analyst_node(state: ResearchState):
    """
    Cross-references the qualitative web findings with the quantitative financial data.
    """
    logger.info("--- ANALYST NODE (CROSS REFERENCING DATA) ---")
    
    findings = state.get("findings", [])
    finance_data = state.get("financial_data", {})
    query = state.get("query", "")
    
    findings_str = "\n\n".join(findings)[:25000]
    finance_str = json.dumps(finance_data, indent=2)
    
    sys_msg = SystemMessage(content="You are a strict quantitative financial analyst.")
    prompt = f"""
    USER QUERY: {query}
    
    QUALITATIVE FINDINGS (Web Research):
    {findings_str}
    
    QUANTITATIVE DATA (yfinance API):
    {finance_str}
    
    Task: Write a highly concise internal synthesis memo cross-referencing the web narrative with the hard mathematical facts. Point out any discrepancies.
    """
    
    try:
        response = await gemini_client.ainvoke([sys_msg, HumanMessage(content=prompt)])
        synthesis = response.content
        if isinstance(synthesis, list):
            synthesis = " ".join([str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in synthesis])
    except Exception as e:
        logger.error(f"Analyst cross-referencing failed: {e}")
        synthesis = "Failed to cross-reference data."
        
    # Append the analyst's synthesis to findings for the generator
    updated_findings = findings + [f"### Quantitative Analyst Synthesis\n{synthesis}"]
    
    return {
        "findings": updated_findings,
        "current_research_step": "analysis_completed"
    }
