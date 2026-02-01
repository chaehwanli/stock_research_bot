from pykrx import stock
from datetime import datetime, timedelta

def get_recent_business_day():
    date = datetime.now()
    # Try up to 5 days back
    for _ in range(5):
        d_str = date.strftime("%Y%m%d")
        try:
            df = stock.get_market_cap_by_ticker(d_str, market="KOSPI")
            if not df.empty:
                return d_str
        except:
            pass
        date -= timedelta(days=1)
    return None

date = get_recent_business_day()
print(f"Using date: {date}")

if date:
    df = stock.get_market_cap_by_ticker(date, market="KOSPI")
    print(df.head())
    
    testers = ["005930", "462330", "305540", "018880"]
    for t in testers:
        if t in df.index:
            print(f"[{t}] Name from Bulk: {df.loc[t, '종목명']}")
        else:
            print(f"[{t}] Not found in KOSPI data")
