import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_moving_averages(hist_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculates the 50-day and 200-day Simple Moving Averages (SMA).
    """
    if hist_df is None or hist_df.empty or len(hist_df) < 50:
        return {"SMA_50": 0.0, "SMA_200": 0.0}
    
    try:
        closes = hist_df['Close']
        sma_50 = float(closes.tail(50).mean())
        sma_200 = float(closes.tail(200).mean()) if len(closes) >= 200 else 0.0
        
        return {
            "SMA_50": round(sma_50, 2),
            "SMA_200": round(sma_200, 2)
        }
    except Exception as e:
        logger.error(f"Failed to calculate moving averages: {e}")
        return {"SMA_50": 0.0, "SMA_200": 0.0}

def calculate_yoy_growth(income_statement: pd.DataFrame, metric_name: str = "Total Revenue") -> Optional[float]:
    """
    Calculates Year-over-Year (YoY) growth for a specific metric in the income statement.
    Expects yfinance income statement dataframe format (columns are dates, most recent first).
    """
    if income_statement is None or income_statement.empty:
        return None
        
    try:
        if metric_name not in income_statement.index:
            return None
            
        metric_data = income_statement.loc[metric_name].dropna()
        if len(metric_data) < 2:
            return None
            
        # yfinance columns are datetime, usually sorted newest to oldest
        current_year_val = float(metric_data.iloc[0])
        previous_year_val = float(metric_data.iloc[1])
        
        if previous_year_val == 0:
            return None
            
        growth = ((current_year_val - previous_year_val) / abs(previous_year_val)) * 100.0
        return round(growth, 2)
        
    except Exception as e:
        logger.error(f"Failed to calculate YoY growth for {metric_name}: {e}")
        return None
