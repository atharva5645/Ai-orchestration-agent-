from app.tools.finance.market_data import get_company_info, get_historical_prices, get_financial_statements
from app.tools.finance.calculations import calculate_moving_averages, calculate_yoy_growth
from app.tools.finance.ratios import extract_key_ratios

def test_finance_module():
    ticker = "AAPL"
    print(f"--- Testing Financial Module for {ticker} ---")
    
    # 1. Market Data
    print("\n[1] Fetching Company Info...")
    info = get_company_info(ticker)
    print(f"Company: {info.get('shortName')} | Sector: {info.get('sector')}")
    print(f"Current Price: ${info.get('currentPrice')} | Market Cap: ${info.get('marketCap')}")
    
    # 2. Historical Prices & MAs
    print("\n[2] Fetching Historical Prices & Moving Averages...")
    hist = get_historical_prices(ticker, period="1y")
    mas = calculate_moving_averages(hist)
    print(f"50-Day SMA: ${mas.get('SMA_50')}")
    print(f"200-Day SMA: ${mas.get('SMA_200')}")
    
    # 3. Financial Statements & YoY Growth
    print("\n[3] Fetching Income Statement & YoY Revenue Growth...")
    statements = get_financial_statements(ticker)
    income_stmt = statements.get("income_statement")
    yoy_growth = calculate_yoy_growth(income_stmt, metric_name="Total Revenue")
    print(f"YoY Revenue Growth: {yoy_growth}%")
    
    # 4. Key Ratios
    print("\n[4] Extracting Key Valuation Ratios...")
    ratios = extract_key_ratios(ticker)
    print(f"Trailing P/E: {ratios.get('Trailing_PE')}")
    print(f"Profit Margin: {ratios.get('Profit_Margin')}%")
    print(f"Return on Equity: {ratios.get('Return_on_Equity')}%")

if __name__ == "__main__":
    test_finance_module()
