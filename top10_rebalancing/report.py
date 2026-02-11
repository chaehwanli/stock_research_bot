
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pykrx import stock
from datetime import datetime
from . import config
import os

class ReportGenerator:
    def __init__(self, backtest_df: pd.DataFrame, top10_history: dict, investment_log: list):
        self.df = backtest_df
        self.top10_history = top10_history
        self.investment_log = investment_log # [(date, amount)]
        self.bench_df = None

    def calculate_benchmark(self):
        """Simulate Monthly DCA on KOSPI Index (1001) using investment_log."""
        if self.df.empty: return

        start_date = self.df.iloc[0]['Date']
        end_date = self.df.iloc[-1]['Date']
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        # Fetch Benchmark (KODEX 200 ETF - 069500)
        print("Fetching Benchmark (KODEX 200) Data...")
        try:
            bench = stock.get_market_ohlcv_by_date(start_str, end_str, "069500")
        except Exception as e:
            print(f"Warning: Benchmark (069500) fetch failed: {e}")
            bench = pd.DataFrame()
        if bench.empty:
            print("Warning: Benchmark fetch failed.")
            return

        # Simulate DCA
        columns = ['Date', 'KOSPI Price', 'Cash', 'Holdings Qty', 'Total Value']
        history = []
        
        current_cash = 0
        current_qty = 0
        
        # Invest Log: Sort by date
        invest_sched = sorted(self.investment_log, key=lambda x: x[0])
        invest_idx = 0
        
        # Iterate through strategy dates to align match
        for date in self.df['Date']:
            # 1. Get Market Price
            try:
                if date in bench.index:
                    price = bench.loc[date]['종가']
                else:
                    # Fallback nearby
                    idx = bench.index.get_indexer([date], method='pad')[0]
                    price = bench.iloc[idx]['종가']
            except:
                price = 0 # Should not happen if range matches
                
            # 2. Check for Investment
            while invest_idx < len(invest_sched) and invest_sched[invest_idx][0] <= date:
                amt = invest_sched[invest_idx][1]
                current_cash += amt
                invest_idx += 1
                
                # Buy immediately?
                if price > 0:
                     qty = current_cash / price # Fractional buy allowed for index simulation
                     current_qty += qty
                     current_cash = 0
            
            total_val = (current_qty * price) + current_cash
            history.append({
                'Date': date,
                'Total Value': total_val
            })
            
        self.bench_df = pd.DataFrame(history)

    def generate_report(self):
        """Generate full markdown report."""
        # Ensure benchmark is calculated
        if self.bench_df is None:
            self.calculate_benchmark()
            
        report = []
        report.append(f"# 📈 Top 10 Equal-Weight Rebalancing Strategy Report")
        report.append(f"**Period:** {self.df['Date'].iloc[0].date()} ~ {self.df['Date'].iloc[-1].date()}")
        report.append(f"**Initial Capital:** {config.INITIAL_CAPITAL:,.0f} KRW")
        report.append(f"**Monthly Contribution:** {config.MONTHLY_CONTRIBUTION:,.0f} KRW")
        
        # 1. Performance Metrics
        start_val = self.df['Total Value'].iloc[0]
        end_val = self.df['Total Value'].iloc[-1]
        
        # Total Invested Calculation
        total_invested = sum([x[1] for x in self.investment_log])
        
        # Simple Return (Total PnL / Total Invested)
        total_profit = end_val - total_invested
        total_return = (total_profit / total_invested) * 100 if total_invested > 0 else 0
        
        # MDD
        roll_max = self.df['Total Value'].cummax()
        daily_drawdown = self.df['Total Value'] / roll_max - 1.0
        mdd = daily_drawdown.min() * 100
        
        report.append(f"## 📊 Performance Summary")
        report.append(f"- **Total Invested Capital:** {total_invested:,.0f} KRW")
        report.append(f"- **Final Portfolio Value:** {end_val:,.0f} KRW")
        report.append(f"- **Net Profit:** {total_profit:,.0f} KRW")
        report.append(f"- **Total Return (on Invested):** {total_return:.2f}%")
        report.append(f"- **Max Drawdown (MDD):** {mdd:.2f}%")
        
        if self.bench_df is not None:
             bench_end = self.bench_df['Total Value'].iloc[-1]
             bench_profit = bench_end - total_invested
             bench_return = (bench_profit / total_invested) * 100 if total_invested > 0 else 0
             report.append(f"- **Benchmark (KOSPI DCA) Value:** {bench_end:,.0f} KRW")
             report.append(f"- **Benchmark Return:** {bench_return:.2f}%")
        
        # 2. Top 10 History Table
        report.append(f"## 📅 Yearly Top 10 Selections")
        report.append(f"| Year | Selected Stocks (Jan) |")
        report.append(f"|---|---|")
        
        for year, df in self.top10_history.items():
            names = df['Name'].tolist() if 'Name' in df.columns else df.index.tolist()
            # Clean names (remove nan)
            names = [str(n) for n in names]
            names_str = ", ".join(names)
            report.append(f"| {year} | {names_str} |")
            
        # 3. Plots
        self.plot_performance()
        report.append(f"## 📈 Equity Curve")
        report.append(f"![Equity Curve](images/top10_equity_curve.png)")
        
        return "\n".join(report)

    def plot_performance(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.df['Date'], self.df['Total Value'], label='Strategy Portfolio')
        
        if self.bench_df is not None:
            plt.plot(self.bench_df['Date'], self.bench_df['Total Value'], label='KOSPI Benchmark (DCA)', linestyle='--', alpha=0.7)
        
        plt.title('Top 10 Equal-Weight Rebalancing Strategy (Monthly DCA)')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value (KRW)')
        plt.legend()
        plt.grid(True)
        
        # Save
        bind_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(bind_dir, 'results')
        images_dir = os.path.join(results_dir, 'images')
        
        os.makedirs(images_dir, exist_ok=True)
        plt.savefig(os.path.join(images_dir, 'top10_equity_curve.png'))
        plt.close()
