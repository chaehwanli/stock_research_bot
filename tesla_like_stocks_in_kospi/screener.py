import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import time
from common_modules.data.market_fetcher import MarketDataFetcher
from pykrx import stock

class TeslaLikeScreener:
    def __init__(self, use_mock=False):
        self.fetcher = MarketDataFetcher(use_mock=use_mock)
        self.use_mock = use_mock
        # Timeframes
        self.end_date_dt = datetime.now()
        self.start_date_dt = self.end_date_dt - timedelta(weeks=14) # ~3.5 months (enough for 12 weeks + buffer)
        
        self.start_date_str = self.start_date_dt.strftime("%Y%m%d")
        self.end_date_str = self.end_date_dt.strftime("%Y%m%d")

    def fetch_kospi_tickers(self):
        """Fetch all KOSPI tickers, excluding ETFs, ETNs, SPACs, and Preferred Stocks via Name."""
        print("Fetching KOSPI tickers...")
        
        # 1. Get All KOSPI Tickers
        all_tickers = self.fetcher.get_all_stocks(market="KOSPI")
        
        filtered_tickers = []
        
        # Keywords to exclude
        etf_brands = ["KODEX", "TIGER", "KBSTAR", "ACE", "HANARO", "SOL", "KOSEF", "ARIRANG", 
                      "TIMEFOLIO", "WOORI", "HANA", "MIGHTY", "FOCUS", "TREX", "HK", "PLUS", "TRUSTON"]
        
        for ticker in all_tickers:
            name = self.fetcher.get_stock_name(ticker)
            
            # 1. Check ETF Brands
            is_etf = any(brand in name for brand in etf_brands)
            
            # 2. Check ETN
            is_etn = "ETN" in name
            
            # 3. Check SPAC
            is_spac = "스팩" in name
            
            # 4. Check Preferred Stock (Ends with '우', '우B', '우(전환)', etc.)
            # Simple heuristic: Ends with '우' or '우B' or contains '우('
            is_preferred = name.endswith("우") or name.endswith("우B") or "우(" in name
            
            if not (is_etf or is_etn or is_spac or is_preferred):
                filtered_tickers.append(ticker)
        
        print(f"  Total: {len(all_tickers)} -> Filtered (Common Stocks Only): {len(filtered_tickers)}")
        return filtered_tickers

    def filter_by_liquidity(self, tickers, min_avg_amount_won=100_000_000_000):
        """
        Filter tickers by Average Daily Trading Value (20d).
        Hard Filter: > 1000억 KRW
        """
        print(f"Filtering {len(tickers)} tickers by liquidity (Min {min_avg_amount_won/1e8}억)...")
        passed_tickers = []
        
        # Batch processing or usage of pykrx's fundamental might be faster, 
        # but let's stick to OHLCV or get_market_cap to be safe and accurate.
        # Ideally, getting all market cap/trading value at once is better.
        
        try:
            # Get Trading Value for a specific Recent Day for ALL tickers at once to save time?
            # pykrx get_market_cap supports "ALL" tickers for a date.
            # But we need 20-day average. 
            # Strategy: Get OHLCV for each ticker is too slow for 900 tickers sequentially.
            # Optimization: Use get_market_cap_by_ticker for specific dates? No.
            # Optimization: Loop is inevitable but we can try to be efficient.
            pass
        except:
            pass

        # For "Average", we really need history.
        # Let's check a specialized pykrx function or just sample the last N days.
        # To speed up, we will FIRST filter by *Today's* or *Yesterday's* trading value lightly (e.g. > 10亿)
        # to remove penny stocks, then calculate accurate 20d avg for candidates.
        
        # Actually, let's just fetch OHLCV for candidates.
        # But fetching OHLCV for 900 items is slow.
        # Alternative: get_market_ohlcv_by_ticker gives values for a range, but one ticker at a time.
        
        # Let's iterate. To avoid blocking for too long, maybe limit to Top Market Cap?
        # No, small caps can be Tesla-like.
        
        # Optimization: Fetch "Trading Value" ranking for a recent day.
        # stock.get_market_trading_value_by_ticker(date, market="KOSPI")
        # this returns valid trading values for all tickers.
        # We can fetch for last 5 days and average them roughly to pre-filter?
        
        print("    Fetching trading values for pre-filtering...")
        # Get yesterday (business day)
        target_dates = []
        curr = self.end_date_dt
        while len(target_dates) < 5:
            curr_str = curr.strftime("%Y%m%d")
            try:
                df = stock.get_market_cap_by_ticker(curr_str, market="KOSPI")
                if not df.empty:
                    target_dates.append(curr_str)
            except:
                pass
            curr -= timedelta(days=1)
            
        # Accumulate trading values
        valid_tickers = set()
        
        # Just use the latest valid day to filter out practically dead stocks first
        # limit to top 50% or something?
        # Let's just strictly implement the 20d avg for a subset or all. 
        
        # Revised approach:
        # 1. Get tickers.
        # 2. Iterate and check. (It might take 5-10 mins for 800 tickers).
        # We need a faster way. 
        # stock.get_market_ohlcv(start, end, ticker)
        
        cnt = 0
        for ticker in tickers:
            # We will catch exceptions inside fetch_data, but here we decide who to fetch.
            # Let's just defer this check to 'fetch_data_and_check_liquidity' combined step
            passed_tickers.append(ticker)
            
        return passed_tickers

    def _calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        # Handle division by zero (if loss is 0, RSI is 100)
        rsi = rsi.fillna(100) # simple fill
        return rsi

    def _calculate_atr_ratio(self, df, period=14):
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # ATR Ratio = ATR / Price
        atr_ratio = atr / df['Close']
        return atr_ratio

    def analyze_ticker(self, ticker, df, skip_liquidity_check=False):
        """
        Calculate metrics for a single ticker dataframe.
        Returns metrics dict or None if insufficient data/liquidity.
        """
        # Rename columns if Korean (pykrx standard)
        rename_map = {
            '시가': 'Open',
            '고가': 'High',
            '저가': 'Low',
            '종가': 'Close',
            '거래량': 'Volume',
            '거래대금': 'Value',
            '등락률': 'Change'
        }
        df = df.rename(columns=rename_map)
        
        # 1. Check Data Length
        if len(df) < 60: # need at least 60 days
            # print(f"[{ticker}] Too short: {len(df)}")
            return None
            
        # 2. Check Liquidity (Last 20 days)
        recent_20 = df.iloc[-20:]
        
        # Determine Amount Column
        avg_amount = 0
        if 'Value' in df.columns: 
             avg_amount = recent_20['Value'].mean()
        else:
             # Fallback
             # print(f"[{ticker}] No trading value column. Cols: {df.columns}")
             avg_amount = (recent_20['Close'] * recent_20['Volume']).mean()

        if not skip_liquidity_check:
            if avg_amount < 100_000_000_000: # 1000억
                return None
        else:
            # Debug: Passed liquidity
            pass

        # 3. Calculate Metrics
        
        # A. Weekly Volatility (12 weeks)
        # Resample to weekly
        df_weekly = df['Close'].resample('W-FRI').last()
        weekly_returns = df_weekly.pct_change().dropna()
        weekly_std = weekly_returns.iloc[-12:].std() # Last 12 weeks
        
        if pd.isna(weekly_std): return None

        # B. Daily Volatility & ATR
        daily_returns = df['Close'].pct_change().dropna()
        daily_std = daily_returns.iloc[-20:].std() # Last 20 days
        
        atr_ratio_series = self._calculate_atr_ratio(df)
        atr_ratio = atr_ratio_series.iloc[-1] # Latest ATR Ratio
        
        if pd.isna(daily_std) or pd.isna(atr_ratio): return None
        
        # C. RSI Volatility (14 days)
        rsi = self._calculate_rsi(df['Close'], period=14)
        rsi_std = rsi.iloc[-14:].std() # Last 14 days standard deviation of RSI
        
        if pd.isna(rsi_std): return None

        return {
            "ticker": ticker,
            "name": self.fetcher.get_stock_name(ticker),
            "weekly_vol": weekly_std,
            "daily_vol": daily_std,
            "atr_ratio": atr_ratio,
            "rsi_std": rsi_std,
            "avg_amount": avg_amount
        }

    def fetch_tesla_benchmark(self):
        """Fetch Tesla data and process same way."""
        print("Fetching Tesla (TSLA) benchmark data...")
        try:
            tsla = yf.Ticker("TSLA")
            # Get data with buffer
            start_date_yf = self.start_date_dt.strftime("%Y-%m-%d")
            df = tsla.history(start=start_date_yf)
            
            # Yfinance columns: Open, High, Low, Close, Volume...
            # Ensure index is datetime (localized? TZ aware?)
            df.index = df.index.tz_localize(None) # Make naive
            
            # Name
            name = "Tesla (Benchmark)"
            
            # Analyze
            metrics = self.analyze_ticker("TSLA", df, skip_liquidity_check=True)
            if metrics:
                metrics['name'] = name
                # Adjust liquidity to KRW? Not strictly necessary for scoring (liquidity is filter), 
                # but good for display. TSLA liquidity is huge, so it passes.
                metrics['avg_amount'] = 9999999999999 # Force pass
                return metrics
        except Exception as e:
            print(f"Failed to fetch Tesla data: {e}")
        return None

    def run(self, limit=None):
        kospi_tickers = self.fetch_kospi_tickers()
        
        if limit and limit > 0:
            print(f"Limiting to first {limit} tickers for speed...")
            kospi_tickers = kospi_tickers[:limit]
        
        print(f"Processing {len(kospi_tickers)} candidates...")
        
        results = []
        
        # Progress bar simple
        total = len(kospi_tickers)
        for i, ticker in enumerate(kospi_tickers):
            if i % 10 == 0:
                print(f"  Processed {i}/{total}...", end='\r')
            
            try:
                df = self.fetcher.get_ohlcv(ticker, self.start_date_str, self.end_date_str)
                if df is None or df.empty:
                    continue
                
                # Pykrx index is datetime
                metrics = self.analyze_ticker(ticker, df)
                if metrics:
                    results.append(metrics)
            except Exception as e:
                 print(f"Err {ticker}: {e}")
                 pass
                 
        print(f"  Processed {total}/{total}. Found {len(results)} valid candidates.")
        
        # Add Tesla
        tsla_metrics = self.fetch_tesla_benchmark()
        if tsla_metrics:
            results.append(tsla_metrics)
            print("Added Tesla to the pool.")
            
        # 4. Compute Scores (Convert to DataFrame)
        df_res = pd.DataFrame(results)
        
        if df_res.empty:
            print("No candidates found.")
            return pd.DataFrame()

        # Compute Ranks (Pct)
        # Higher is better
        df_res['rank_weekly'] = df_res['weekly_vol'].rank(pct=True)
        df_res['rank_daily_mix'] = (df_res['daily_vol'] + df_res['atr_ratio']).rank(pct=True)
        df_res['rank_rsi'] = df_res['rsi_std'].rank(pct=True) # Higher RSI std = more oscillation
        
        # Formula:
        # TVS = 0.4 * DailyMix + 0.3 * RSI + 0.3 * Weekly
        df_res['TVS'] = (
            0.40 * df_res['rank_daily_mix'] +
            0.30 * df_res['rank_rsi'] +
            0.30 * df_res['rank_weekly']
        ) * 100
        
        # Sort
        df_res = df_res.sort_values(by='TVS', ascending=False).reset_index(drop=True)
        
        return df_res

if __name__ == "__main__":
    screener = TeslaLikeScreener()
    df = screener.run()
    print(df[['ticker', 'name', 'TVS', 'weekly_vol', 'rsi_std', 'avg_amount']].head(20))
