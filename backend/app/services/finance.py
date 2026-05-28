import yfinance as yf
from typing import Dict, Any, Optional

class FinanceService:
    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive ticker info for a given stock symbol.
        """
        ticker = yf.Ticker(symbol)
        return ticker.info

    def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[Any]:
        """
        Get historical market data.
        """
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        # Convert to dictionary or list of records
        return hist.reset_index().to_dict('records')

finance_service = FinanceService()
