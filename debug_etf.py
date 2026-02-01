from pykrx import stock
from datetime import datetime, timedelta

def get_recent_business_day():
    date = datetime.now()
    # Try up to 400 days back (in case system time is far future)
    for i in range(400):
        d_str = date.strftime("%Y%m%d")
        try:
            l = stock.get_etf_ticker_list(d_str)
            if l:
                return d_str
        except:
            pass
        date -= timedelta(days=1)
    return None

today = datetime.now().strftime("%Y%m%d")
print(f"Testing today ({today}):")
try:
    l = stock.get_etf_ticker_list(today)
    print(f"Success: {len(l)} ETFs")
except Exception as e:
    print(f"Failed: {e}")

recent = get_recent_business_day()
print(f"Testing recent business day ({recent}):")
if recent:
    l = stock.get_etf_ticker_list(recent)
    print(f"Success: {len(l)} ETFs")
