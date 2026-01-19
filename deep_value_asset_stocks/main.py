import sys
import os
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.dart_fetcher import DartFetcher
from data.market_fetcher import MarketDataFetcher
from logic.screener import Screener
from llm.llm_client import LLMClient
from llm.prompts import REPORT_PROMPT
from notification.telegram_bot import TelegramNotifier

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
    market = MarketDataFetcher(use_mock=use_mock)
    screener = Screener(dart, market)
    llm = LLMClient()
    notifier = TelegramNotifier()
    
    # 2. Screening
    tickers = market.get_all_stocks()
    print(f"Scanning {len(tickers)} tickers...")
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
