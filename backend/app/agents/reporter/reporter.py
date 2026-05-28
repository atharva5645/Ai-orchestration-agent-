import logging
from langchain_core.messages import SystemMessage, HumanMessage
from app.state.research_state import ResearchState
from app.agents.shared.llm import gemini_client

logger = logging.getLogger(__name__)

REPORTER_SYSTEM_PROMPT = """You are an elite Wall Street Financial Analyst and Expert Copywriter.
Your task is to synthesize raw research findings, market data, and quantitative financial metrics into a professional, investor-grade Research Report.

You MUST use Markdown formatting and strictly adhere to the following 10-section structure. Do not skip any sections.

# [Company/Asset Name] - Comprehensive Research Report

## 1. Executive Summary
Provide a high-level overview of the asset, its current market position, and the core thesis of the research.

## 2. Market Overview
Describe the broader macroeconomic environment, sector conditions, and total addressable market (TAM).

## 3. Company Analysis
Detail the company's business model, revenue streams, and core operations.

## 4. Financial Metrics
Synthesize the quantitative financial data provided. Highlight PE ratio, EBITDA, revenue growth, margins, and market capitalization. Explain what these numbers indicate about the company's health.

## 5. Competitor Comparison
Compare the asset against key industry rivals. Highlight competitive advantages (moats) or disadvantages.

## 6. Key Trends
Identify technological, regulatory, or consumer trends impacting the asset.

## 7. Risks
Detail material risks including market risks, operational risks, and regulatory threats.

## 8. Opportunities
Highlight growth avenues, potential expansions, or upcoming catalysts.

## 9. Future Outlook
Provide a forward-looking synthesis. Where is the asset heading in the next 1-3 years?

## 10. Sources
List the exact sources and URLs used to compile this report (extracted from the search history).

Rules:
- Use professional, objective, and analytical tone.
- Do not hallucinate financial data. If specific numbers are not provided in the context, explicitly state "Data not available."
- Format beautifully with bullet points, bold text for emphasis, and clear spacing.
"""

async def reporter_node(state: ResearchState):
    """
    Synthesizes the final markdown report from all gathered research.
    """
    logger.info("Generating final investor-grade report...")

    # Compile the raw context
    findings = "\n".join(state.get("findings", []))
    financial_data = state.get("financial_data", {})
    history = state.get("search_history", [])
    
    # Format financial data nicely
    finance_str = "No specific quantitative financial data extracted."
    if financial_data:
        finance_str = "Extracted Financial Data:\n"
        for k, v in financial_data.items():
            finance_str += f"- {k}: {v}\n"
            
    sources_str = "Search History/Sources:\n" + "\n".join([f"- {s}" for s in history])

    # Construct the user prompt
    user_prompt = f"""
Please generate the final research report based on the following context.

[QUALITATIVE FINDINGS]
{findings}

[QUANTITATIVE FINANCIAL DATA]
{finance_str}

[SOURCES]
{sources_str}
"""

    messages = [
        SystemMessage(content=REPORTER_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ]

    # Generate the report
    response = await gemini_client.ainvoke(messages)
    final_report = response.content

    logger.info("Report generation complete.")
    
    # Update state
    return {
        "final_report": final_report,
        "current_research_step": "generation_complete"
    }
