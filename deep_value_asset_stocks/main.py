import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path to import common_modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common_modules.data.dart_fetcher import DartFetcher
from common_modules.data.market_fetcher import MarketDataFetcher
from common_modules.llm.llm_client import LLMClient
from common_modules.notification.telegram_bot import TelegramNotifier
from src.logic.screener import Screener
from src.llm.prompts import REPORT_PROMPT

def save_results_to_csv(results, filename="results.csv"):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Results saved to {filename}")
    return filename

def main():
    print(">>> Deep Value Asset Stock Bot Started")
    
    # 1. Initialize Modules
    # Check if we should use Mock mode
    # For now, let's default to Mock if DART_API_KEY is not set or if explictly requested
    dart_key = os.getenv("DART_API_KEY")
    use_mock = False
    if not dart_key or dart_key == "your_dart_api_key":
        print("Using MOCK Mode (DART Key not valid)")
        use_mock = True
        dart_key = "MOCK"
    
    dart = DartFetcher(api_key=dart_key)
    
    # Check if DartFetcher fell back to MOCK mode
    if dart.api_key == "MOCK" and not use_mock:
        print("DartFetcher switched to MOCK mode. Switching MarketDataFetcher to MOCK mode as well.")
        use_mock = True
        
    market = MarketDataFetcher(use_mock=use_mock)
    screener = Screener(dart, market)
    llm = LLMClient()
    notifier = TelegramNotifier()
    
    # 2. Screening
    tickers = market.get_all_stocks()
    print(f"Scanning {len(tickers)} tickers...")
    
    # Fallback to Mock if Real Mode returns 0 tickers (e.g. pykrx failure)
    if not tickers and not use_mock:
        print("Warning: Real Mode found 0 tickers (Market Data Error). Switching to MOCK Mode.")
        use_mock = True
        # Re-initialize modules in Mock Mode
        dart.api_key = "MOCK"
        dart.load_mock_data()
        market = MarketDataFetcher(use_mock=True)
        screener = Screener(dart, market)
        tickers = market.get_all_stocks()
        print(f"Scanning {len(tickers)} tickers (MOCK)...")
        
    candidates = screener.run_screening(tickers)
    
    if not candidates:
        print("No candidates found.")
        notifier.send_message("Deep Value Bot: No candidates found today.")
        return

    # 3. LLM Analysis & Reporting
    full_report = f"Subject: Deep Value Asset Stock Report ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    full_report += f"Found {len(candidates)} candidates.\n\n"
    
    for candidate in candidates:
        print(f"Analyzing {candidate['name']}...")
        report = llm.analyze_company(candidate, REPORT_PROMPT)
        
        # If LLM fails (e.g. quota), use fallback text
        if "Error" in report:
            report = f"# Report for {candidate['name']}\n(LLM Analysis Failed: {report})\n"
            report += f"PBR: {candidate['pbr']}, Cash Ratio: {candidate['cash_ratio']:.2%}"

        full_report += report + "\n\n" + ("="*20) + "\n\n"

    # 4. Notification
    print("Sending Notification...")
    notifier.send_message(full_report)
    
    # Save CSV
    csv_file = save_results_to_csv(candidates)
    # notifier.send_file(csv_file) # Optional: send CSV

    print(">>> Job Completed.")

if __name__ == "__main__":
    main()
