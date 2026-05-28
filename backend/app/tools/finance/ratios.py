import yfinance as yf
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def extract_key_ratios(ticker_symbol: str) -> Dict[str, Optional[float]]:
    """
    Extracts deterministic valuation ratios directly from yfinance.
    We prefer standard calculated values provided by the exchange data.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        return {
            "Trailing_PE": info.get("trailingPE"),
            "Forward_PE": info.get("forwardPE"),
            "PEG_Ratio": info.get("pegRatio"),
            "Price_to_Book": info.get("priceToBook"),
            "Debt_to_Equity": info.get("debtToEquity"),
            "Return_on_Equity": info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None,
            "Profit_Margin": info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None,
            "Operating_Margin": info.get("operatingMargins", 0) * 100 if info.get("operatingMargins") else None,
            "EBITDA": info.get("ebitda")
        }
    except Exception as e:
        logger.error(f"Failed to extract ratios for {ticker_symbol}: {e}")
        return {}
