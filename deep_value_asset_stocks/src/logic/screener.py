from datetime import datetime
import pandas as pd

class Screener:
    def __init__(self, dart_fetcher, market_fetcher):
        self.dart = dart_fetcher
        self.market = market_fetcher
        self.results = []

    def run_screening(self, tickers):
        print(f"Starting screening for {len(tickers)} tickers...")
        candidates = []
        stats = {
            "total_scanned": len(tickers),
            "passed_pbr": 0,
            "passed_profit": 0,
            "passed_cash": 0,
            "passed_shareholder": 0,
            "final_candidates": 0
        }
        
        for ticker in tickers:
            corp_name = self.market.get_stock_name(ticker)
            print(f"Checking {corp_name} ({ticker})...")
            
            # 1. PBR Check
            pbr_ok, pbr_val = self.check_pbr(ticker)
            if not pbr_ok:
                print(f"  -> Failed PBR: {pbr_val}")
                continue
            stats["passed_pbr"] += 1
            
            # Get Corp Code for DART
            corp_code = self.dart.find_corp_code(corp_name)
            if not corp_code:
                print(f"  -> Failed to find Corp Code for {corp_name}")
                continue
            
            # 2. Consecutive Profit Check
            profit_ok, profit_history = self.check_consecutive_profit(corp_code)
            if not profit_ok:
                 print(f"  -> Failed Profit Check")
                 continue
            stats["passed_profit"] += 1
            
            # 3. Cash Ratio Check
            cash_ok, cash_ratio = self.check_cash_ratio(corp_code)
            if not cash_ok:
                print(f"  -> Failed Cash Ratio Check: {cash_ratio}")
                continue
            stats["passed_cash"] += 1

            # 4. Shareholder Check
            share_ok, share_sum = self.check_shareholder_ownership(corp_code)
            if not share_ok:
                print(f"  -> Failed Shareholder Check: {share_sum}%")
                continue
            stats["passed_shareholder"] += 1

            # If all passed
            print(f"  -> PASSED ALL CHECKS!")
            candidates.append({
                "ticker": ticker,
                "name": corp_name,
                "pbr": pbr_val,
                "profit_history": profit_history,
                "cash_ratio": cash_ratio,
                "shareholder_stake": share_sum
            })
        
        stats["final_candidates"] = len(candidates)
        return candidates, stats

    def check_pbr(self, ticker):
        fund = self.market.get_fundamental(ticker)
        if fund is None:
            return False, "No Data"
        try:
            pbr = float(fund["PBR"])
            return (pbr <= 0.6), pbr
        except:
            return False, "Error"

    def check_consecutive_profit(self, corp_code):
        # Check last 5 years: 2020~2024 (assuming we are in early 2026, 2024 might be out, but let's check available)
        years = [2020, 2021, 2022, 2023, 2024]
        profit_history = {}
        
        for year in years:
            fs = self.dart.get_financial_summary(corp_code, year)
            if fs is None or fs.empty:
                return False, f"Missing Data {year}"
            
            # Find Operating Income
            # Account names can vary: 영업이익, Operating Income
            # Mock data uses '영업이익'
            try:
                op_income_row = fs[fs['account_nm'].str.contains('영업이익|Operating Income')]
                if op_income_row.empty:
                     return False, f"No Op Income {year}"
                
                amount_str = op_income_row.iloc[0]['thstrm_amount'].replace(',', '')
                op_income = float(amount_str)
                profit_history[year] = op_income
                
                if op_income <= 0:
                    return False, "Loss"
            except Exception as e:
                return False, f"Error {year}"

        return True, profit_history

    def check_cash_ratio(self, corp_code):
        # Check latest year (e.g., 2023)
        target_year = 2023 
        fs = self.dart.get_financial_summary(corp_code, target_year)
        if fs is None or fs.empty:
            return False, "No Data"
        
        try:
            # Get Total Assets
            assets_row = fs[fs['account_nm'].str.contains('자산총계|Total Assets')]
            assets = float(assets_row.iloc[0]['thstrm_amount'].replace(',', ''))
            
            # Get Cash & Equivalents
            cash_row = fs[fs['account_nm'].str.contains('현금및현금성자산|Cash')]
            cash = 0
            if not cash_row.empty:
                cash = float(cash_row.iloc[0]['thstrm_amount'].replace(',', ''))
            
            # Get Short-term Financial Assets
            short_fin_row = fs[fs['account_nm'].str.contains('단기금융|Short-term Financial')]
            short_fin = 0
            if not short_fin_row.empty:
                short_fin = float(short_fin_row.iloc[0]['thstrm_amount'].replace(',', ''))
                
            total_liquid = cash + short_fin
            ratio = total_liquid / assets
            
            # Threshold: let's use 30% as placeholder, or maybe 20%? User said "High".
            # Implementation Plan said 30% default.
            return (ratio >= 0.3), ratio
            
        except Exception as e:
            print(f"Cash Check Error: {e}")
            return False, "Error"

    def check_shareholder_ownership(self, corp_code):
        df = self.dart.get_major_shareholders(corp_code)
        if df is None or df.empty:
            return False, "No Data"
        
        try:
            # Filter for "Major Shareholder" and "Related Party"
            # In DART major_shareholders, it usually lists them.
            # We can just sum up the 'stock_qota' (Stake Ratio) of the top list or filter by relation.
            # For simplicity in mock/MVP, sum all listed in the table provided by DART major_shareholders API
            # typically returns the list of major shareholders and related parties.
            
            # Column 'stock_qota' is stake percentage.
            # Mock data returns float, real data might obtain string.
            
            total_stake = 0
            for index, row in df.iterrows():
                try:
                    val = row['stock_qota']
                    if isinstance(val, str):
                        val = float(val.replace(',', ''))
                    total_stake += val
                except:
                    continue
            
            # Use max(total_stake) if duplicates exist?
            # Dart API returns list. Usually sum of unique holders.
            # Let's assume the sum is correct.
            
            return (total_stake >= 30.0), total_stake
            
        except Exception as e:
            return False, f"Error: {e}"
