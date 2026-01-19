import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.dart_fetcher import DartFetcher
from data.market_fetcher import MarketDataFetcher
from logic.screener import Screener
from llm.llm_client import LLMClient
from llm.prompts import REPORT_PROMPT

def main():
    print(">>> Initializing Modules (MOCK MODE)...")
    dart = DartFetcher(api_key="MOCK")
    market = MarketDataFetcher(use_mock=True)
    screener = Screener(dart, market)
    llm = LLMClient()
    
    # 1. Get Tickers
    tickers = market.get_all_stocks()
    
    # 2. Run Screener
    print("\n>>> Running Screener...")
    results = screener.run_screening(tickers)
    print(f"Screener found {len(results)} candidates.")
    
    # 3. Run LLM Analysis
    print("\n>>> Running LLM Analysis...")
    if not results:
        print("No candidates to analyze.")
        return

    for candidate in results:
        print(f"--- Analyzing {candidate['name']} ---")
        report = llm.analyze_company(candidate, REPORT_PROMPT)
        print(report)
        print("-" * 30)

if __name__ == "__main__":
    main()
