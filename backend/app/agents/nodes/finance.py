import logging
from typing import Dict, Any
from app.state.research_state import ResearchState
from app.tools.finance.market_data import get_company_info

logger = logging.getLogger(__name__)

async def finance_node(state: ResearchState) -> Dict[str, Any]:
    """
    Extracts numerical financial data deterministically using yfinance.
    Uses the ticker identified by the router_planner.
    """
    logger.info("--- FINANCE NODE (QUANTITATIVE ANALYSIS) ---")
    
    company_symbol = state.get("company_symbol", "")
    extracted_ticker = state.get("extracted_ticker", "")
    query = state.get("query", "")
    sector = state.get("sector_classification", "")
    financial_data = {}
    final_ticker = "NONE"
    
    if company_symbol and company_symbol.upper() != "NONE":
        final_ticker = company_symbol.upper()
        logger.info(f"Using company_symbol from API request: {final_ticker}")
    elif extracted_ticker and extracted_ticker.upper() != "NONE":
        final_ticker = extracted_ticker.upper()
        logger.info(f"Using extracted_ticker from LLM router: {final_ticker}")
    else:
        logger.info("No ticker found in API request or LLM extraction, assuming NONE.")

    # Fetch Data if Ticker Exists
    if final_ticker != "NONE":
        logger.info(f"Extracting deterministic financial data for {final_ticker}...")
        
        # Indian ticker detection logic
        indian_keywords = ["india", "indian", "nse", "bse", "nifty", "sensex"]
        indian_sectors = ["Banking", "IT", "Pharma", "FMCG", "Auto"]
        
        query_lower = query.lower()
        is_indian_context = any(kw in query_lower for kw in indian_keywords) or (sector in indian_sectors)
        
        info = None
        try:
            if not (final_ticker.endswith(".NS") or final_ticker.endswith(".BO")) and is_indian_context:
                logger.info(f"Indian context detected. Trying {final_ticker}.NS first...")
                info = get_company_info(f"{final_ticker}.NS")
                if info:
                    final_ticker = f"{final_ticker}.NS"
                else:
                    logger.info(f"{final_ticker}.NS failed, trying {final_ticker}.BO...")
                    info = get_company_info(f"{final_ticker}.BO")
                    if info:
                        final_ticker = f"{final_ticker}.BO"
            
            # If still no info or not Indian context, try the original ticker
            if not info:
                info = get_company_info(final_ticker)

            if info:
                financial_data = {
                    "marketCap": info.get("marketCap"),
                    "forwardPE": info.get("forwardPE"),
                    "trailingPE": info.get("trailingPE"),
                    "profitMargins": info.get("profitMargins"),
                    "52WeekHigh": info.get("fiftyTwoWeekHigh"),
                    "52WeekLow": info.get("fiftyTwoWeekLow"),
                    "dividendYield": info.get("dividendYield"),
                    "revenueGrowth": info.get("revenueGrowth")
                }
                logger.info(f"Successfully fetched financial data for {final_ticker}")
            else:
                logger.warning(f"No company info returned for {final_ticker}")
        except Exception as e:
            logger.error(f"Error fetching financial data for {final_ticker}: {e}")
            financial_data = {"error": f"Failed to fetch data for {final_ticker}"}

    return {
        "financial_data": financial_data,
        "ticker": final_ticker,
        "current_research_step": "finance_completed"
    }
