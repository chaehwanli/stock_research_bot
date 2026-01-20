import sys
import os

# Add current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from common_modules.data.market_fetcher import MarketDataFetcher

def test_fetcher():
    print("Initializing MarketDataFetcher...")
    fetcher = MarketDataFetcher(use_mock=False)
    
    print("Calling get_all_stocks()...")
    tickers = fetcher.get_all_stocks(market="ALL")
    
    print(f"Got {len(tickers)} tickers.")
    if len(tickers) > 0:
        print(f"First 5 tickers: {tickers[:5]}")
        print("SUCCESS")
    else:
        print("FAILURE: Still got 0 tickers.")

if __name__ == "__main__":
    test_fetcher()
