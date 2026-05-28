import yfinance as yf
print("Fetching AAPL info...")
try:
    ticker = yf.Ticker("AAPL")
    print(ticker.info.get("shortName"))
except Exception as e:
    print(f"yfinance error: {e}")
print("Fetching HDFC silver etf...")
try:
    # "provide me hdfc silver price" might resolve to something weird
    # let's test what the LLM might have extracted
    pass
except Exception as e:
    print(e)
