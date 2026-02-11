import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from common_modules.data.market_fetcher import MarketDataFetcher
    from common_modules.publishing.wiki_publisher import WikiPublisher
    from active_etfs.config import TARGET_ETFS, WIKI_PAGE_TITLE
    from active_etfs.analysis import ETFAnalyzer
    from active_etfs.report import ReportGenerator
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

try:
    from pykrx import etf
except ImportError:
    etf = None

def main():
    print(f"Starting Active ETF Evaluation for {len(TARGET_ETFS)} ETFs...")
    
    # Initialize components
    fetcher = MarketDataFetcher()
    analyzer = ETFAnalyzer()
    
    # Date Range: 1 Year
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    
    results = []
    all_attachments = []
    images_map = {} # Ticker -> [image_files]
    
    for ticker, config_name in TARGET_ETFS.items():
        # Use configured name
        name = config_name
        
        # If config is just ticker or empty, try fetching dynamically
        if not name or name == str(ticker):
            if etf:
                try:
                    fetched = etf.get_etf_ticker_name(ticker)
                    if fetched and fetched != str(ticker):
                         name = fetched
                except Exception:
                    pass
            
            if not name or name == str(ticker):
                 fetched = fetcher.get_stock_name(ticker)
                 if fetched and fetched != str(ticker):
                      name = fetched
                 
        print(f"Processing {name} ({ticker})...")
        
        # 1. Fetch Data
        ohlcv_df = None
        if etf:
            try:
                ohlcv_df = etf.get_etf_ohlcv_by_date(start_date, end_date, ticker)
            except Exception as e:
                print(f"etf module failed for {ticker}: {e}")
                
        if ohlcv_df is None or ohlcv_df.empty:
             ohlcv_df = fetcher.get_ohlcv(ticker, start_date, end_date)
             
        fundamental_df = fetcher.get_fundamental(ticker) # Fetch generic fundamental
        
        if ohlcv_df is None or ohlcv_df.empty:
            print(f"Failed to fetch data for {ticker}")
            continue
            
        # Standardize Columns
        # etf module uses different columns? usually it matches unless specified
        col_map = {
            '시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume',
            '거래대금': 'Trading Value', '등락률': 'Change',
            '기초지수': 'Index', 'NAV': 'NAV'
        }
        if ohlcv_df is not None:
             ohlcv_df = ohlcv_df.rename(columns=col_map)
        
        # Ensure required columns exist
        required_cols = ['Close', 'High', 'Low', 'Volume']
        if not all(col in ohlcv_df.columns for col in required_cols):
            print(f"Missing required columns for {ticker}. Available: {ohlcv_df.columns}")
            continue

        try:
            # 2. Analyze
            metrics = analyzer.calculate_metrics(ohlcv_df, fundamental_df, ticker, name)
            if metrics:
                results.append(metrics)
                
            # 3. Generate Plots
            images = analyzer.generate_plots(ohlcv_df, ticker, name)
            if images:
                # images are filenames in active_etfs/results/images/
                # We need full paths for attachments
                full_paths = [os.path.join(analyzer.images_dir, img) for img in images]
                all_attachments.extend(full_paths)
                images_map[ticker] = images
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
            
    if not results:
        print("No results generated.")
        return

    # 4. Generate Report
    print("Generating Report...")
    report_gen = ReportGenerator(WIKI_PAGE_TITLE)
    report_gen.add_summary_table(results)
    report_gen.add_details(results, images_map)
    
    report_content = report_gen.get_markdown()
    
    # 5. Publish to Wiki
    print("Publishing to Wiki...")
    publisher = WikiPublisher()
    
    # Check if we should publish (env var check inside publisher)
    url = publisher.publish_report(report_content, WIKI_PAGE_TITLE, attachments=all_attachments)
    
    if url:
        print(f"Report published successfully: {url}")
    else:
        print("Failed to publish report or Wiki not configured.")

if __name__ == "__main__":
    main()
