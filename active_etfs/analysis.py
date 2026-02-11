import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

class ETFAnalyzer:
    def __init__(self):
        self.results_dir = os.path.join(os.path.dirname(__file__), "results")
        self.images_dir = os.path.join(self.results_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)

    def calculate_metrics(self, ohlcv_df, fundamental_df, ticker, name):
        """
        Calculate performance metrics for an ETF.
        """
        if ohlcv_df is None or ohlcv_df.empty:
            return None
            
        # Map Korean columns if necessary
        col_map = {
            '시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume',
            '거래대금': 'Trading Value', '등락률': 'Change'
        }
        ohlcv_df = ohlcv_df.rename(columns=col_map)
        
        # Ensure required columns exist
        required_cols = ['Close', 'High', 'Low', 'Volume']
        if not all(col in ohlcv_df.columns for col in required_cols):
            print(f"Missing columns for {ticker}. Available: {ohlcv_df.columns}")
            return None

        # 1-Year Return
        try:
            current_price = ohlcv_df['Close'].iloc[-1]
            start_price = ohlcv_df['Close'].iloc[0]
            returns = ((current_price - start_price) / start_price) * 100
        except KeyError:
             print(f"KeyError: 'Close' column not found in {ticker} data. Columns: {ohlcv_df.columns}")
             return None

        # High/Low
        high_price = ohlcv_df['High'].max()
        low_price = ohlcv_df['Low'].min()

        # Avg Volume & Transaction Value
        avg_volume = ohlcv_df['Volume'].mean()
        
        # Estimate Transaction Value
        avg_tx_value = 0
        if 'Trading Value' in ohlcv_df.columns:
             avg_tx_value = ohlcv_df['Trading Value'].mean()
        elif 'Close' in ohlcv_df.columns and 'Volume' in ohlcv_df.columns:
             avg_tx_value = (ohlcv_df['Close'] * ohlcv_df['Volume']).mean()

        dividend = 0
        if fundamental_df is not None:
             # Basic check for dividend columns
             if 'DIV' in fundamental_df:
                 dividend = fundamental_df['DIV']
             elif 'DPS' in fundamental_df:
                 dividend = fundamental_df['DPS']

        return {
            "Ticker": ticker,
            "Name": name,
            "Current Price": current_price,
            "1Y Return (%)": round(returns, 2),
            "1Y High": high_price,
            "1Y Low": low_price,
            "Avg Volume": int(avg_volume),
            "Avg Tx Value": int(avg_tx_value),
            "Dividend": dividend
        }

    def generate_plots(self, ohlcv_df, ticker, name):
        """
        Generate and save plots for the ETF.
        """
        if ohlcv_df is None or ohlcv_df.empty:
            return []

        generated_files = []
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 1. Price History
        plt.figure(figsize=(10, 5))
        plt.plot(ohlcv_df.index, ohlcv_df['Close'], label='Close Price')
        plt.title(f"{name} ({ticker}) - 1 Year Price History")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()
        
        filename = f"{ticker}_price_{date_str}.png"
        filepath = os.path.join(self.images_dir, filename)
        plt.savefig(filepath)
        plt.close()
        generated_files.append(filename)

        # 2. Volume History
        plt.figure(figsize=(10, 5))
        plt.bar(ohlcv_df.index, ohlcv_df['Volume'], color='orange', label='Volume')
        plt.title(f"{name} ({ticker}) - 1 Year Volume History")
        plt.xlabel("Date")
        plt.ylabel("Volume")
        plt.grid(True)
        plt.legend()
        
        filename = f"{ticker}_volume_{date_str}.png"
        filepath = os.path.join(self.images_dir, filename)
        plt.savefig(filepath)
        plt.close()
        generated_files.append(filename)
        
        return generated_files
