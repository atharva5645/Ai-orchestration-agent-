import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_company_info(ticker_symbol: str) -> Dict[str, Any]:
    """
    Retrieve basic company information and current market data.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Extract core data safely
        return {
            "symbol": info.get("symbol", ticker_symbol),
            "shortName": info.get("shortName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "currentPrice": info.get("currentPrice", 0.0),
            "marketCap": info.get("marketCap", 0),
            "currency": info.get("currency", "USD"),
            "description": info.get("longBusinessSummary", "")
        }
    except Exception as e:
        logger.error(f"Failed to retrieve company info for {ticker_symbol}: {e}")
        return {"error": str(e)}

def get_historical_prices(ticker_symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """
    Retrieve historical price data for calculations.
    Period options: 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        return hist
    except Exception as e:
        logger.error(f"Failed to retrieve historical prices for {ticker_symbol}: {e}")
        return None

def get_financial_statements(ticker_symbol: str) -> Dict[str, Optional[pd.DataFrame]]:
    """
    Retrieves Income Statement, Balance Sheet, and Cash Flow.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        return {
            "income_statement": ticker.financials,
            "balance_sheet": ticker.balance_sheet,
            "cash_flow": ticker.cashflow
        }
    except Exception as e:
        logger.error(f"Failed to retrieve financials for {ticker_symbol}: {e}")
        return {"income_statement": None, "balance_sheet": None, "cash_flow": None}
