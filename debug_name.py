from pykrx import stock

tickers = ["005930", "462330", "305540", "018880"]

print("Testing get_market_ticker_name:")
for t in tickers:
    try:
        name = stock.get_market_ticker_name(t)
        print(f"[{t}] Market Name: '{name}' (Type: {type(name)})")
    except Exception as e:
        print(f"[{t}] Market Error: {e}")

print("\nTesting get_etf_ticker_name:")
for t in tickers:
    try:
        name = stock.get_etf_ticker_name(t)
        print(f"[{t}] ETF Name: '{name}'")
    except Exception as e:
        print(f"[{t}] ETF Error: {e}")
