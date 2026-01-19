from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta

class MarketDataFetcher:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        # Simple mock data for market metrics
        self.mock_market_data = {
            "005930": {"pbr": 1.2, "market_cap": 400000000000000, "close": 70000},
            "000000": {"pbr": 0.15, "market_cap": 25000000000, "close": 2500} # Deep Value Corp: PBR < 0.2
        }

    def get_fundamental(self, ticker, date=None):
        """
        Retrieves fundamental data (PBR, PER, EPS, BPS, DIV, etc.) for a specific date.
        If date is None, uses today (or nearest trading day).
        """
        if self.use_mock:
            if ticker in self.mock_market_data:
                data = self.mock_market_data[ticker]
                # Return as Series to match pykrx output format roughly
                return pd.Series({
                    "PBR": data["pbr"],
                    "PER": 10.0,
                    "DIV": 3.0,
                    "BPS": data["close"] / data["pbr"]
                })
            return None

        if date is None:
            date = datetime.now().strftime("%Y%m%d")
        
        try:
            # get_market_fundamental accepts (date, ticker) or (date, date, ticker)
            # We just want specific date snapshot
            df = stock.get_market_fundamental(date, date, ticker)
            if df is None or df.empty:
                 # Try previous days if today is holiday
                 for i in range(1, 5):
                     prev_date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
                     df = stock.get_market_fundamental(prev_date, prev_date, ticker)
                     if not df.empty:
                         return df.iloc[-1]
            if not df.empty:
                return df.iloc[-1]
            return None
        except Exception as e:
            print(f"Error fetching fundamental for {ticker}: {e}")
            return None

    def get_ohlcv(self, ticker, start_date, end_date):
        """
        Retrieves OHLCV data.
        """
        if self.use_mock:
            # Return dummy dataframe
            dates = pd.date_range(start_date, end_date)
            df = pd.DataFrame(index=dates, columns=["Open", "High", "Low", "Close", "Volume"])
            df["Close"] = 1000
            if ticker in self.mock_market_data:
                 df["Close"] = self.mock_market_data[ticker]["close"]
            return df

        try:
            df = stock.get_market_ohlcv(start_date, end_date, ticker)
            return df
        except Exception as e:
             print(f"Error fetching OHLCV for {ticker}: {e}")
             return None

    def get_all_stocks(self, market="ALL"):
        """
        Get list of all tickers. market can be KOSPI, KOSDAQ, ALL.
        """
        if self.use_mock:
            return list(self.mock_market_data.keys())

        try:
            tickers = stock.get_market_ticker_list(market=market)
            return tickers
        except Exception as e:
            print(f"Error fetching ticker list: {e}")
            return []

    def get_stock_name(self, ticker):
        if self.use_mock:
            if ticker == "005930": return "Samsung Electronics"
            if ticker == "000000": return "Deep Value Corp"
            return "Unknown"

        try:
            return stock.get_market_ticker_name(ticker)
        except:
            return None
