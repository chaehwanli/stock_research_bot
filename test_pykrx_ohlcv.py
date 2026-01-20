from pykrx import stock

try:
    print("Testing OHLCV for 005930 (Samsung Elecs)...")
    df = stock.get_market_ohlcv("20250101", "20250110", "005930")
    print(df)
    if df is not None and not df.empty:
        print("OHLCV fetch success")
    else:
        print("OHLCV fetch returned empty")
except Exception as e:
    print(f"OHLCV error: {e}")
