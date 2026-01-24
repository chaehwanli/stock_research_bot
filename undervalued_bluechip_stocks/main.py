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
    candidates, all_results, stats = screener.run_screening(tickers)
    
    if not all_results:
        print("No candidates found. Proceeding to report empty results.")
        # Do not return, let it publish the empty report


    # 3. Reporting
    print(f"Found {len(candidates)} candidates.")
    
    # Prepare Report Content
    from common_modules.reporting.report_generator import ReportGenerator
    # Note: ReportGenerator generic enough?
    # It expects llm_reports list of strings.
    # We have candidates with 'total_score', 'grade', 'details' containing reasoning.
    
    llm_reports = []
    formatted_candidates = []
    
    
    # Sort all results by Total Score descending
    all_results.sort(key=lambda x: x['total_score'], reverse=True)
    
    for c in all_results:
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
        report_section += f"- **Qual Breakdown**:\n\n"
        report_section += f"| Criterion | Score |\n"
        report_section += f"|---|---|\n"
        report_section += f"| Duplicate Listing | {details['duplicate_listing']}pts |\n"
        report_section += f"| Global Brand | {details['global_brand']}pts |\n"
        report_section += f"| Profit Sustainability | {details['profit_sustainability']}pts |\n"
        report_section += f"| Future Growth | {details['growth_potential']}pts |\n"
        report_section += f"| Management | {details['management']}pts |\n"
        report_section += f"\n**LLM Reasoning**:\n{reasoning}\n"
        
        llm_reports.append(report_section)
        
        # Candidate table data - ONLY for Top Candidates (Grade A/B)
        if c['grade'] in ['A', 'B']:
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
    
    # helper for rate
    def calc_rate(val, total):
        if total == 0: return "0.0"
        return f"{(val/total)*100:.1f}"

    scanned = stats.get('scanned', 0)
    passed_quant = stats.get('passed_quant', 0)
    analyzed_llm = stats.get('analyzed_llm', passed_quant)
    passed_final = stats.get('passed_final', 0)

    full_report += "## 1. Screening Summary (Funnel)\n"
    full_report += "| Stage | Count | Pass Rate |\n"
    full_report += "|---|---|---|\n"
    full_report += f"| Total Scanned | {scanned} | 100% |\n"
    full_report += f"| Passed Quant (PER<20, PBR<1.5) | {passed_quant} | {calc_rate(passed_quant, scanned)}% |\n"
    if analyzed_llm != passed_quant:
        full_report += f"| Selected for LLM (Sampled) | {analyzed_llm} | - |\n"
    full_report += f"| **Final Candidates** (Grade B+) | **{passed_final}** | {calc_rate(passed_final, analyzed_llm)}% |\n\n"
    
    full_report += "## 2. Selected for LLM List\n"
    full_report += "| Ticker | Name | Grade | Quant Score (PER+PBR) | PER | PBR | Reason by LLM |\n"
    full_report += "|---|---|---|---|---|---|---|\n"
    for c in all_results:
        # Quant Score = score_per + score_pbr
        q_score = c['score_per'] + c['score_pbr']
        reason = c['details'].get('llm_reasoning', 'No reasoning').replace('\n', ' ').replace('|', '-')[:100] + "..." # Truncate for table
        full_report += f"| {c['ticker']} | {c['name']} | {c['grade']} | {q_score} | {c['details']['per']} | {c['details']['pbr']} | {reason} |\n"
    
    full_report += "\n"
    
    full_report += "\n"
    
    full_report += "\n## 3. Detailed Analysis\n\n"
    if not llm_reports:
        full_report += "No candidates found to analyze.\n"
    for report in llm_reports:
        full_report += report + "\n---\n\n"

    # 4.Publish to Wiki
    from common_modules.publishing.wiki_publisher import WikiPublisher
    publisher = WikiPublisher()
    # Add time to avoid overlap
    page_title = f"Bluechip_Report_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
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
