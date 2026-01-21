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
from undervalued_bluechip_stocks.src.screener_bluechip import BluechipScreener

def save_results_to_csv(results, filename="bluechip_results.csv"):
    df = pd.DataFrame(results)
    # Flatten details dict if possible, or just dump
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Results saved to {filename}")
    return filename

def main():
    print(">>> Undervalued Bluechip Stock Bot Started")
    
    # 1. Initialize Modules
    dart_key = os.getenv("DART_API_KEY")
    use_mock = False
    if not dart_key or dart_key == "your_dart_api_key":
        print("Using MOCK Mode (DART Key not valid)")
        use_mock = True
        dart_key = "MOCK"
        
    dart = DartFetcher(api_key=dart_key)
    
    # If DART falls back to Mock, force Market to Mock
    if dart.api_key == "MOCK" and not use_mock:
        use_mock = True
    
    market = MarketDataFetcher(use_mock=use_mock)
    llm = LLMClient()
    notifier = TelegramNotifier()
    screener = BluechipScreener(dart, market, llm)
    
    # 2. Screening
    tickers = market.get_all_stocks()
    print(f"Scanning {len(tickers)} tickers...")
    
    # Fallback to Mock if Real Mode returns 0
    if not tickers and not use_mock:
        print("Warning: Real Mode 0 tickers. Switching to Mock.")
        use_mock = True
        dart.api_key = "MOCK"
        dart.load_mock_data()
        market = MarketDataFetcher(use_mock=True)
        screener = BluechipScreener(dart, market, llm)
        tickers = market.get_all_stocks()
    
    # Run Screener
    candidates, stats = screener.run_screening(tickers)
    
    if not candidates:
        print("No candidates found.")
        notifier.send_message("Bluechip Bot: No candidates found today.")
        return

    # 3. Reporting
    print(f"Found {len(candidates)} candidates.")
    
    # Prepare Report Content
    from common_modules.reporting.report_generator import ReportGenerator
    # Note: ReportGenerator generic enough?
    # It expects llm_reports list of strings.
    # We have candidates with 'total_score', 'grade', 'details' containing reasoning.
    
    llm_reports = []
    formatted_candidates = []
    
    for c in candidates:
        # Format candidate for ReportGenerator (needs specific keys)
        # ReportGenerator expects: ticker, name, pbr, cash_ratio, shareholder_stake
        # Our Bluechip candidate has: ticker, name, score_per, score_pbr, score_qual, total_score, grade, details
        
        # We need to adapt or update ReportGenerator.
        # ReportGenerator is tightly coupled to "Deep Value" logic (cash_ratio, stake).
        # We should probably create a specific report generator for Bluechip or make it generic.
        # For now, let's create a custom report string here or extend ReportGenerator.
        
        # Custom Report Construction for Bluechip
        details = c['details']
        reasoning = details.get('llm_reasoning', 'No reasoning')
        
        report_section = f"### {c['name']} ({c['ticker']}) - Grade {c['grade']} ({c['total_score']}pts)\n"
        report_section += f"- **Stats**: PER {details['per']}, PBR {details['pbr']}\n"
        report_section += f"- **Scores**: PER+PBR (Quant) {c['score_per']+c['score_pbr']} + Qual {c['score_qual']}\n"
        report_section += f"- **Qual Breakdown**:\n"
        report_section += f"  - Duplicate Listing: {details['duplicate_listing']}pts\n"
        report_section += f"  - Global Brand: {details['global_brand']}pts\n"
        report_section += f"  - Profit Sustainability: {details['profit_sustainability']}pts\n"
        report_section += f"  - Future Growth: {details['growth_potential']}pts\n"
        report_section += f"  - Management: {details['management']}pts\n"
        report_section += f"\n**LLM Reasoning**:\n{reasoning}\n"
        
        llm_reports.append(report_section)
        
        # Candidate table data
        formatted_candidates.append({
            "ticker": c['ticker'],
            "name": c['name'],
            "grade": c['grade'],
            "score": c['total_score'],
            "per": details['per'],
            "pbr": details['pbr']
        })

    # Create Custom Markdown Report
    full_report = f"# Undervalued Bluechip Report ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    full_report += f"**Scanned**: {stats['scanned']} | **Passed Quant**: {stats['passed_quant']} | **Final Candidates**: {stats['passed_final']}\n\n"
    
    full_report += "## Top Candidates\n"
    full_report += "| Ticker | Name | Grade | Score | PER | PBR |\n"
    full_report += "|---|---|---|---|---|---|\n"
    for fc in formatted_candidates:
        full_report += f"| {fc['ticker']} | {fc['name']} | **{fc['grade']}** | {fc['score']} | {fc['per']} | {fc['pbr']} |\n"
    full_report += "\n"
    
    full_report += "## Detailed Analysis\n\n"
    for report in llm_reports:
        full_report += report + "\n---\n\n"

    # 4. Publish to Wiki (First, to get the link)
    from common_modules.publishing.wiki_publisher import WikiPublisher
    publisher = WikiPublisher()
    page_title = f"Bluechip_Report_{datetime.now().strftime('%Y-%m-%d')}"
    wiki_url = publisher.publish_report(full_report, page_title)
    
    # 5. Notification
    print("Sending Notification...")
    summary = f"Bluechip Bot: Found {len(candidates)} candidates.\n"
    for c in formatted_candidates:
        summary += f"- {c['name']}: {c['grade']} ({c['score']}pts)\n"
    
    if wiki_url and isinstance(wiki_url, str):
        summary += f"\n[Full Report]({wiki_url})"
    
    notifier.send_message(summary)

    save_results_to_csv(candidates)
    print(">>> Job Completed.")

if __name__ == "__main__":
    main()
