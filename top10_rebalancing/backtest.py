
import pandas as pd
import numpy as np
from pykrx import stock
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from . import config

class Backtester:
    def __init__(self):
        self.portfolio = {}  # {ticker: quantity}
        self.cash = config.INITIAL_CAPITAL
        self.history = []  # List of daily stats
        self.top10_history = {}  # {year: dataframe of top 10}
        self.trading_days = []
        self.price_cache = {} # {ticker: dataframe} - Cached OHLCV
        self.investment_log = [] # [(date, amount)]
        
        # Historical Top 10 (Approximate Jan 1st Rankings)
        # Manually curated due to pykrx market cap fetch failure.
        # Excludes Preferred Shares (e.g. Samsung Elec Pfd).
        self.HISTORICAL_TOP10 = {
            2016: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "005380": "Hyundai Motor", 
                "028260": "Samsung C&T", "035420": "NAVER", "090430": "AmorePacific", 
                "051910": "LG Chem", "032830": "Samsung Life", "000270": "Kia", "005490": "POSCO Holdings"
            },
            2017: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "005380": "Hyundai Motor", 
                "035420": "NAVER", "005490": "POSCO Holdings", "028260": "Samsung C&T", 
                "055550": "Shinhan Financial", "051910": "LG Chem", "012330": "Hyundai Mobis", "105560": "KB Financial"
            },
            2018: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "068270": "Celltrion", 
                "207940": "Samsung Biologics", "005380": "Hyundai Motor", "051910": "LG Chem", 
                "005490": "POSCO Holdings", "105560": "KB Financial", "035420": "NAVER", "028260": "Samsung C&T"
            },
            2019: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "035420": "NAVER", 
                "207940": "Samsung Biologics", "005380": "Hyundai Motor", "012330": "Hyundai Mobis", 
                "068270": "Celltrion", "051910": "LG Chem", "005490": "POSCO Holdings", "055550": "Shinhan Financial"
            },
            2020: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "051910": "LG Chem", 
                "207940": "Samsung Biologics", "068270": "Celltrion", "035420": "NAVER", 
                "006400": "Samsung SDI", "005380": "Hyundai Motor", "035720": "Kakao", "012330": "Hyundai Mobis"
            },
            2021: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "035420": "NAVER", 
                "051910": "LG Chem", "005380": "Hyundai Motor", "207940": "Samsung Biologics", 
                "006400": "Samsung SDI", "035720": "Kakao", "068270": "Celltrion", "005490": "POSCO Holdings"
            },
            2022: {
                 "005930": "Samsung Electronics", "373220": "LG Energy Solution", "000660": "SK Hynix", 
                 "207940": "Samsung Biologics", "005380": "Hyundai Motor", "035420": "NAVER", 
                 "006400": "Samsung SDI", "000270": "Kia", "005490": "POSCO Holdings", "051910": "LG Chem"
            },
            2023: {
                "005930": "Samsung Electronics", "373220": "LG Energy Solution", "000660": "SK Hynix", 
                "207940": "Samsung Biologics", "051910": "LG Chem", "006400": "Samsung SDI", 
                "005380": "Hyundai Motor", "035420": "NAVER", "000270": "Kia", "005490": "POSCO Holdings"
            },
            2024: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "373220": "LG Energy Solution", 
                "207940": "Samsung Biologics", "005380": "Hyundai Motor", "000270": "Kia", 
                "005490": "POSCO Holdings", "035420": "NAVER", "051910": "LG Chem", "006400": "Samsung SDI"
            },
            2025: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "373220": "LG Energy Solution", 
                "207940": "Samsung Biologics", "005380": "Hyundai Motor", "000270": "Kia", 
                "105560": "KB Financial", "005490": "POSCO Holdings", "035420": "NAVER", "068270": "Celltrion"
            },
            # 2026 Use 2025 list or updated? Use 2025 for simplicity as rebal is early Jan
            2026: {
                "005930": "Samsung Electronics", "000660": "SK Hynix", "373220": "LG Energy Solution", 
                "207940": "Samsung Biologics", "005380": "Hyundai Motor", "000270": "Kia", 
                "105560": "KB Financial", "005490": "POSCO Holdings", "035420": "NAVER", "068270": "Celltrion"
            }
        }

    def _get_trading_days(self, start_date, end_date):
        """Fetch all KOSPI trading days in range."""
        df = stock.get_market_ohlcv_by_date(start_date, end_date, "005930")
        return df.index.to_list()

    def _find_target_date(self, year, month, week_ordinal, weekday, valid_dates):
        """Find specific trading day (e.g., 2nd Monday)."""
        c = calendar.Calendar(firstweekday=0)
        month_cal = c.monthdatescalendar(year, month)
        
        days = [d for week in month_cal for d in week if d.month == month and d.weekday() == weekday]
        
        if len(days) < week_ordinal:
            target_py_date = days[-1]
        else:
            target_py_date = days[week_ordinal - 1]
            
        target_ts = pd.Timestamp(target_py_date)
        
        for d in valid_dates:
            if d >= target_ts:
                return d
        
        return valid_dates[-1] 

    def run(self):
        end_date = datetime.now()
        start_date = end_date - relativedelta(years=config.START_YEAR_OFFSET)
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        print(f"Fetching Trading Days ({start_str} ~ {end_str})...")
        self.trading_days = self._get_trading_days(start_str, end_str)
        if not self.trading_days:
            raise ValueError("No trading days found.")
            
        current_date_idx = 0
        
        # Pre-fetch Prices for ALL tickers in HISTORICAL_TOP10
        all_tickers = set()
        for year, year_map in self.HISTORICAL_TOP10.items():
            all_tickers.update(year_map.keys())
            
        print(f"Pre-fetching prices for {len(all_tickers)} unique tickers (10 Years)...")
        # Optimization: Fetch full range once for all unique tickers
        self._ensure_price_cache(list(all_tickers), start_date, end_date)
        
        # Initial Setup (Year 1)
        first_year = self.trading_days[0].year
        next_rebal_date = self._find_target_date(
            first_year, config.REBALANCING_MONTH, config.REBALANCING_WEEK, config.REBALANCING_WEEKDAY, self.trading_days
        )
        
        self.investment_log.append((next_rebal_date, config.INITIAL_CAPITAL))
        
        print(f"Start Backtest from {next_rebal_date.date()}")
        
        while current_date_idx < len(self.trading_days) and self.trading_days[current_date_idx] < next_rebal_date:
            current_date_idx += 1
            
        while current_date_idx < len(self.trading_days):
            today = self.trading_days[current_date_idx]
            
            target_rebal = self._find_target_date(
                today.year, config.REBALANCING_MONTH, config.REBALANCING_WEEK, config.REBALANCING_WEEKDAY, self.trading_days
            )
            target_invest = self._find_target_date(
                today.year, today.month, config.INVESTMENT_WEEK, config.INVESTMENT_WEEKDAY, self.trading_days
            )
            
            if today == target_rebal:
                self._rebalance(today)
            elif today == target_invest:
                self._invest_monthly(today)
                
            self._update_daily_value(today)
            
            current_date_idx += 1
            
        return pd.DataFrame(self.history)

    def _ensure_price_cache(self, tickers, start_date, end_date):
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        for ticker in tickers:
            if ticker not in self.price_cache:
                try:
                    df = stock.get_market_ohlcv_by_date(start_str, end_str, ticker)
                    self.price_cache[ticker] = df
                except Exception as e:
                    print(f"Error caching price for {ticker}: {e}")
                    self.price_cache[ticker] = pd.DataFrame()

    def _fetch_price_from_cache(self, ticker, date):
        if ticker in self.price_cache:
            df = self.price_cache[ticker]
            if date in df.index:
                return df.loc[date]['종가']
        return 0

    def _rebalance(self, date):
        print(f"[Rebalance] {date.date()} ...")
        
        # 1. Sell Current Holdings
        current_holdings_val = 0
        sold_amount = 0
        if self.portfolio:
            for ticker, qty in self.portfolio.items():
                price = self._fetch_price_from_cache(ticker, date)
                if price == 0:
                     try: 
                        df = stock.get_market_ohlcv(date.strftime("%Y%m%d"), date.strftime("%Y%m%d"), ticker)
                        if not df.empty: price = df['종가'].iloc[0]
                     except: pass
                
                if price > 0:
                    amount = price * qty
                    sold_amount += amount
            
            fee = sold_amount * config.TRANSACTION_FEE
            net_proceeds = sold_amount - fee
            self.cash += net_proceeds
            self.portfolio = {} # Clear

        # 2. Add Monthly Contribution
        is_first = (len(self.history) == 0)
        if not is_first:
            amt = config.MONTHLY_CONTRIBUTION
            self.cash += amt
            self.investment_log.append((date, amt))
            print(f"  + Added Monthly Contribution: {amt:,.0f} KRW")

        # 3. Select New Top 10 (Historical Data)
        top10_df = self._fetch_top10(date)
        if top10_df.empty:
            print(f"  Warning: No Top 10 data for {date.year}")
            return

        self.top10_history[date.year] = top10_df
        target_tickers = top10_df.index.tolist()
        
        # 4. Buy New Portfolio
        allocation_per_stock = self.cash / len(target_tickers)
        total_buy_cost = 0
        
        for ticker in target_tickers:
            price = self._fetch_price_from_cache(ticker, date)
            if price > 0:
                qty = int(allocation_per_stock // price)
                if qty > 0:
                    cost = qty * price
                    self.portfolio[ticker] = qty
                    total_buy_cost += cost
        
        self.cash -= total_buy_cost
        print(f"  > Rebalance Complete. Portfolio Value: {total_buy_cost:,.0f}, Cash: {self.cash:,.0f}")

    def _invest_monthly(self, date):
        amt = config.MONTHLY_CONTRIBUTION
        self.cash += amt
        self.investment_log.append((date, amt))
        
        if not self.portfolio:
            return
            
        target_tickers = list(self.portfolio.keys())
        allocation_per_stock = config.MONTHLY_CONTRIBUTION / len(target_tickers)
        
        total_buy_cost = 0
        for ticker in target_tickers:
            price = self._fetch_price_from_cache(ticker, date)
            if price == 0:
                 try:
                    df = stock.get_market_ohlcv(date.strftime("%Y%m%d"), date.strftime("%Y%m%d"), ticker)
                    if not df.empty: price = df['종가'].iloc[0]
                 except: pass

            if price > 0:
                qty = int(allocation_per_stock // price)
                if qty > 0:
                    cost = qty * price
                    self.portfolio[ticker] += qty
                    total_buy_cost += cost
        
        self.cash -= total_buy_cost

    def _fetch_top10(self, date):
        """Fetch Top 10 stocks (Historical Dict)."""
        year = date.year
        
        # Fallback closest year if exact year missing (e.g. out of range)
        if year not in self.HISTORICAL_TOP10:
             # Find closest year available
             years = sorted(self.HISTORICAL_TOP10.keys())
             closest_year = min(years, key=lambda x: abs(x - year))
             print(f"Warning: Year {year} Top 10 missing. Using {closest_year}")
             year = closest_year
             
        data = self.HISTORICAL_TOP10[year]
        df = pd.DataFrame(index=list(data.keys()))
        df['Name'] = list(data.values())
        return df

    def _update_daily_value(self, date):
        current_holdings_value = 0
        for ticker, qty in self.portfolio.items():
            price = self._fetch_price_from_cache(ticker, date)
            if price == 0 and ticker in self.price_cache:
                try:
                    df = self.price_cache[ticker]
                    idx_loc = df.index.get_indexer([date], method='pad')[0]
                    if idx_loc != -1:
                        price = df['종가'].iloc[idx_loc]
                    else:
                        # Case: Before listing date? Use 0 or first price?
                        # If price is truly 0, asset value is 0.Correct.
                        pass 
                except: pass
            
            current_holdings_value += price * qty
            
        total_asset = self.cash + current_holdings_value
        
        self.history.append({
            "Date": date,
            "Total Value": total_asset,
            "Cash": self.cash,
            "Holdings Value": current_holdings_value
        })

    def get_investment_log(self):
        return getattr(self, 'investment_log', [])
