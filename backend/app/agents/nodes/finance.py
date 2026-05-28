import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

from app.state.research_state import ResearchState
from app.agents.shared.llm import gemini_client

from app.tools.finance.market_data import get_company_info, get_historical_prices, get_financial_statements
from app.tools.finance.calculations import calculate_moving_averages, calculate_yoy_growth
from app.tools.finance.ratios import extract_key_ratios

logger = logging.getLogger(__name__)

class TickerExtraction(BaseModel):
    has_ticker: bool = Field(description="True if a public company ticker symbol was mentioned.")
    ticker_symbol: str = Field(description="The primary stock ticker symbol (e.g. AAPL, TSLA). Empty if none.")

async def finance_node(state: ResearchState) -> Dict[str, Any]:
    """
    Extracts numerical financial data deterministically using yfinance.
    """
    logger.info("--- FINANCE NODE (QUANTITATIVE ANALYSIS) ---")
    query = state.get("query", "")
    
    # 1. Extract Ticker
    sys_msg = SystemMessage(content="You extract stock ticker symbols from user queries.")
    prompt = f"Query: {query}\nExtract the primary public company ticker symbol."
    
    try:
        extraction = await gemini_client.ainvoke_structured(
            messages=[sys_msg, HumanMessage(content=prompt)],
            schema=TickerExtraction
        )
    except Exception as e:
        logger.error(f"Failed to extract ticker: {e}")
        extraction = TickerExtraction(has_ticker=False, ticker_symbol="")
        
    financial_data = {}
    
    # 2. Fetch Data if Ticker Exists
    if extraction.has_ticker and extraction.ticker_symbol:
        ticker = extraction.ticker_symbol.upper()
        logger.info(f"Extracting deterministic financial data for {ticker}...")
        
        info = get_company_info(ticker)
        ratios = extract_key_ratios(ticker)
        
        hist = get_historical_prices(ticker, "1y")
        mas = calculate_moving_averages(hist)
        
        statements = get_financial_statements(ticker)
        yoy_revenue = calculate_yoy_growth(statements.get("income_statement"), "Total Revenue")
        
        financial_data = {
            "ticker": ticker,
            "company_name": info.get("shortName"),
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "trailing_pe": ratios.get("Trailing_PE"),
            "profit_margin_pct": ratios.get("Profit_Margin"),
            "return_on_equity_pct": ratios.get("Return_on_Equity"),
            "sma_50": mas.get("SMA_50"),
            "sma_200": mas.get("SMA_200"),
            "yoy_revenue_growth_pct": yoy_revenue
        }
        logger.info(f"Financial Data Retrieved: {financial_data}")
    else:
        logger.info("No specific ticker found. Skipping yfinance extraction.")
        
    return {
        "financial_data": financial_data,
        "current_research_step": "finance_analysis_completed"
    }
