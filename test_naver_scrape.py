import requests
from bs4 import BeautifulSoup
import re

def fetch_naver_tickers(sosok):
    # sosok: 0 for KOSPI, 1 for KOSDAQ
    url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page=1"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Get last page number
    try:
        last_page_node = soup.select_one(".pgRR a")
        if last_page_node:
            last_page_url = last_page_node['href']
            last_page = int(re.search(r'page=(\d+)', last_page_url).group(1))
        else:
            last_page = 1
    except Exception as e:
        print(f"Error finding last page: {e}")
        last_page = 1
        
    print(f"Sosok {sosok}: Found {last_page} pages.")
    
    tickers = []
    # For testing, just scrape 1 page
    for page in range(1, 2): 
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        items = soup.select("table.type_2 tbody tr")
        for item in items:
            # Check if valid row
            if len(item.select("td")) < 2: 
                continue
                
            link = item.select_one("a.tltle")
            if link:
                code = re.search(r'code=(\d+)', link['href']).group(1)
                name = link.text.strip()
                tickers.append(code)
                
    return tickers

print("Fetching KOSPI...")
kospi = fetch_naver_tickers(0)
print(f"Fetched {len(kospi)} KOSPI tickers from page 1. First 5: {kospi[:5]}")

print("Fetching KOSDAQ...")
kosdaq = fetch_naver_tickers(1)
print(f"Fetched {len(kosdaq)} KOSDAQ tickers from page 1. First 5: {kosdaq[:5]}")
