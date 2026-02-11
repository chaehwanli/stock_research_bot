
import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from top10_rebalancing.backtest import Backtester
from top10_rebalancing.report import ReportGenerator

def main():
    print("="*60)
    print("🚀 Running Top 10 Equal-Weight Rebalancing Strategy Backtest")
    print("="*60)
    
    try:
        # 1. Run Backtest
        bt = Backtester()
        print("Starting simulation...")
        history_df = bt.run()
        
        investment_log = bt.get_investment_log()
        top10_history = bt.top10_history
        
        print("\nBacktest Complete.")
        print(f"Total Trading Days: {len(history_df)}")
        print(f"Final Portfolio Value: {history_df['Total Value'].iloc[-1]:,.0f} KRW")
        
        # 2. Generate Report
        print("\nGenerating Performance Report...")
        reporter = ReportGenerator(history_df, top10_history, investment_log)
        report_md = reporter.generate_report()
        
        # 3. Save Results
        bind_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir = os.path.join(bind_dir, 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        report_path = os.path.join(results_dir, "top10_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)
            
        print(f"✅ Report saved to: {report_path}")
        print(f"✅ Equity Curve saved to: {os.path.join(results_dir, 'images', 'top10_equity_curve.png')}")
        
        # Also save history data
        csv_path = os.path.join(results_dir, "top10_history.csv")
        history_df.to_csv(csv_path, index=False)
        print(f"✅ History data saved to: {csv_path}")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
