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
        
    candidate_list, stats = screener.run_screening(tickers)
    
    # 3. LLM Analysis & Reporting
    print(f"Found {len(candidate_list)} candidates.")
    
    llm_reports = []
    for candidate in candidate_list:
        print(f"Analyzing {candidate['name']}...")
        report = llm.analyze_company(candidate, REPORT_PROMPT)
        
        # If LLM fails (e.g. quota), use fallback text
        if "Error" in report:
            fallback = f"### {candidate['name']} (Analysis Failed)\nError: {report}\n\n"
            fallback += f"- PBR: {candidate['pbr']}\n- Cash Ratio: {candidate['cash_ratio']:.2%}"
            llm_reports.append(fallback)
        else:
            llm_reports.append(report)

    # Generate Markdown Report
    from common_modules.reporting.report_generator import ReportGenerator
    reporter = ReportGenerator()
    full_report = reporter.generate_markdown_report(stats, candidate_list, llm_reports)
    
    # 4. Publish to Wiki (First, to get the link)
    from common_modules.publishing.wiki_publisher import WikiPublisher
    publisher = WikiPublisher()
    # Add time to avoid overlap: Report_YYYY-MM-DD_HHMM
    page_title = f"Report_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
    wiki_url = publisher.publish_report(full_report, page_title)
    
    # 5. Notification
    print("Sending Notification...")
    # Summary message construction
    summary_msg = f"Deep Value Bot Report ({datetime.now().strftime('%Y-%m-%d')})\n"
    summary_msg += f"Scanned: {stats['total_scanned']}, Candidates: {stats['final_candidates']}\n\n"
    for c in candidate_list:
        summary_msg += f"- {c['name']} ({c['ticker']}): PBR {c['pbr']}\n"
    
    if wiki_url and isinstance(wiki_url, str):
        summary_msg += f"\n[Full Report]({wiki_url})"
        
    notifier.send_message(summary_msg)

    # Save CSV
    csv_file = save_results_to_csv(candidate_list)
    print(">>> Job Completed.")

if __name__ == "__main__":
    main()
