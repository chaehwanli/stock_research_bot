from pykrx import stock
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re

class MarketDataFetcher:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        # Simple mock data for market metrics
        self.mock_market_data = {
            "005930": {"pbr": 1.2, "market_cap": 400000000000000, "close": 70000},
            "000000": {"pbr": 0.15, "market_cap": 25000000000, "close": 2500} # Deep Value Corp: PBR < 0.2
        }
        self.ticker_name_cache = {} # Cache for stock names

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
            
            # If still empty after retries, trigger fallback
            raise Exception("pykrx returned empty data")
            
        except Exception as e:
            # Fallback to Naver Finance if pykrx fails
            print(f"pykrx failed for {ticker} ({e}). Attempting fallback to Naver Finance for Fundamental data...")
            return self._fetch_fundamental_naver(ticker)
            


    def _fetch_fundamental_naver(self, ticker):
        """
        Fallback method to fetch fundamental data (PBR, PER, DIV) from Naver Finance
        """
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            pbr = 0.0
            per = 0.0
            div = 0.0
            
            pbr_elem = soup.select_one("#_pbr")
            if pbr_elem:
                txt = pbr_elem.text.replace(',', '').strip()
                if txt: pbr = float(txt)
                
            per_elem = soup.select_one("#_per")
            if per_elem:
                txt = per_elem.text.replace(',', '').strip()
                if txt: per = float(txt)
            
            dvr_elem = soup.select_one("#_dvr")
            if dvr_elem:
                txt = dvr_elem.text.replace(',', '').strip()
                if txt: div = float(txt)
                
            # If we got at least PBR, return as Series
            if pbr > 0 or per > 0:
                return pd.Series({
                    "PBR": pbr,
                    "PER": per,
                    "DIV": div,
                    "BPS": 0 # Not easily available via simple ID, but PBR is what we need mostly
                })
                
            return None
        except Exception as e:
            print(f"Error fetching Naver Finance fundamental for {ticker}: {e}")
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

        # Try fetching tickers for today and look back up to 5 days if it fails
        for i in range(5):
            target_date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            try:
                tickers = stock.get_market_ticker_list(target_date, market=market)
                if tickers:
                    return tickers
            except Exception as e:
                if i == 4: # Last attempt
                    print(f"Error fetching ticker list: {e}")
        
        if not tickers:
            print("pykrx returned 0 tickers. Attempting fallback to Naver Finance...")
            tickers = self._fetch_tickers_naver(market)

        return tickers

    def _fetch_tickers_naver(self, market):
        """
        Fallback method to fetch tickers from Naver Finance
        """
        print(f"Fetching {market} tickers from Naver Finance...")
        tickers = []
        
        # market codes for Naver: 0=KOSPI, 1=KOSDAQ
        sosok_list = []
        if market == "KOSPI" or market == "ALL":
            sosok_list.append(0)
        if market == "KOSDAQ" or market == "ALL":
            sosok_list.append(1)
            
        for sosok in sosok_list:
            try:
                # 1. Get last page number
                base_url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}"
                res = requests.get(base_url + "&page=1")
                soup = BeautifulSoup(res.text, 'html.parser')
                
                last_page = 1
                last_page_node = soup.select_one(".pgRR a")
                if last_page_node:
                    last_page_url = last_page_node['href']
                    match = re.search(r'page=(\d+)', last_page_url)
                    if match:
                        last_page = int(match.group(1))
                
                print(f"Naver Finance (sosok={sosok}): Found {last_page} pages.")
                
                # 2. Scrape all pages
                for page in range(1, last_page + 1):
                    url = f"{base_url}&page={page}"
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    
                    items = soup.select("table.type_2 tbody tr")
                    for item in items:
                        if len(item.select("td")) < 2: 
                            continue
                        
                        link = item.select_one("a.tltle")
                        if link:
                            code_match = re.search(r'code=(\d+)', link['href'])
                            if code_match:
                                code = code_match.group(1)
                                name = link.text.strip()
                                tickers.append(code)
                                self.ticker_name_cache[code] = name
                                
            except Exception as e:
                print(f"Error scraping Naver Finance (sosok={sosok}): {e}")
                
        # Remove duplicates just in case
        return list(set(tickers))

    def _fetch_name_naver(self, ticker):
        """
        Fallback method to fetch stock name from Naver Finance
        """
        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Selector for name: .wrap_company h2 a
            name_elem = soup.select_one(".wrap_company h2 a")
            if name_elem:
                return name_elem.text.strip()
            
            # Alternative selector just in case
            name_elem = soup.select_one(".wrap_company h2")
            if name_elem:
                 # Check if it has 'a' tag inside, if not take text
                 if not name_elem.find('a'):
                     return name_elem.text.strip()
            
            return None
        except Exception as e:
            print(f"Error fetching Naver Finance name for {ticker}: {e}")
            return None

    def get_stock_name(self, ticker):
        if self.use_mock:
            if ticker == "005930": return "Samsung Electronics"
            if ticker == "000000": return "Deep Value Corp"
            return "Unknown"

        try:
            # Check cache first (populated by Naver fallback)
            if ticker in self.ticker_name_cache:
                return self.ticker_name_cache[ticker]

            name = stock.get_market_ticker_name(ticker)
            
            # Check if it returned a DataFrame (known pykrx issue sometimes)
            if isinstance(name, pd.DataFrame):
                 if not name.empty:
                      name = str(name.iloc[0, 0])
                 else:
                      name = str(ticker)
            
            # If name is empty or same as ticker, try Naver
            if not name or str(name) == str(ticker):
                 naver_name = self._fetch_name_naver(ticker)
                 if naver_name:
                     self.ticker_name_cache[ticker] = naver_name
                     return naver_name

            return str(name) if name else str(ticker)
        except:
            # Fallback to Naver if pykrx fails completely
            naver_name = self._fetch_name_naver(ticker)
            if naver_name:
                 self.ticker_name_cache[ticker] = naver_name
                 return naver_name
            return str(ticker)
