import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data.dart_fetcher import DartFetcher
from data.market_fetcher import MarketDataFetcher
from logic.screener import Screener

def main():
    print("Initializing Fetchers in MOCK mode...")
    dart = DartFetcher(api_key="MOCK")
    market = MarketDataFetcher(use_mock=True)
    
    screener = Screener(dart, market)
    
    # Get all mock tickers
    tickers = market.get_all_stocks()
    print(f"Test Tickers: {tickers}")
    
    # Run screening
    results = screener.run_screening(tickers)
    
    print("\nXXX Screening Results XXX")
    for res in results:
        print(f"PASSED: {res['name']} ({res['ticker']})")
        print(f" - PBR: {res['pbr']}")
        print(f" - Cash Ratio: {res['cash_ratio']:.2%}")
        print(f" - Shareholder Stake: {res['shareholder_stake']}%")

if __name__ == "__main__":
    main()
