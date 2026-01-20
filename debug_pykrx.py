from pykrx import stock
from datetime import datetime, timedelta

print(f"Current Time: {datetime.now()}")

for i in range(5):
    target_date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
    print(f"Trying date: {target_date}")
    try:
        tickers = stock.get_market_ticker_list(target_date, market="ALL")
        print(f"Date: {target_date}, Ticker count: {len(tickers)}")
        if tickers:
            print(f"First 5 tickers: {tickers[:5]}")
            break
    except Exception as e:
        print(f"Error on {target_date}: {e}")
