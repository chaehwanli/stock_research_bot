from pykrx import stock
import requests
from bs4 import BeautifulSoup

print("Testing pykrx for 20250101...")
try:
    tickers = stock.get_market_ticker_list("20250101", market="ALL")
    print(f"20250101 tickers: {len(tickers)}")
except Exception as e:
    print(f"pykrx error: {e}")

print("\nChecking requests and bs4...")
print(f"requests version: {requests.__version__}")
try:
    print(f"BeautifulSoup version: {BeautifulSoup.__version__}") # BeautifulSoup usually doesn't expose version directly this way sometimes, but let's try
except:
    import bs4
    print(f"bs4 version: {bs4.__version__}")
