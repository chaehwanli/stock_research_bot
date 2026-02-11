from pykrx import stock
import pykrx.etf as etf
import pandas as pd
from datetime import datetime, timedelta

end_date = datetime.now().strftime("%Y%m%d")
start_date = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")

ticker = "443290" # KODEX K-Robot Active
print(f"Fetching {ticker} from {start_date} to {end_date} using etf module")
# etf.get_etf_ohlcv_by_ticker is likely the function or get_etf_ohlcv_by_date
# pykrx docs: get_etf_ohlcv_by_ticker(start, end, ticker)
try:
    df = etf.get_etf_ohlcv_by_date(start_date, end_date, ticker)
    print(df)
except Exception as e:
    print(f"Error: {e}")

ticker = "069500" # KODEX 200
print(f"Fetching {ticker} from {start_date} to {end_date} using etf module")
try:
    df = etf.get_etf_ohlcv_by_date(start_date, end_date, ticker)
    print(df)
except Exception as e:
    print(f"Error: {e}")
