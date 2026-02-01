# Implementation Log

## [2026-02-01:22:12] Tesla-like Stock Screener Walkthrough

This document explains how to use the new Stock Screener designed to identify "Tesla-like" high-volatility stocks in the KOSPI market.

### 1. Concept

The screener finds stocks that behave like **Tesla (TSLA)**—characterized by high volatility, frequent price reversals, and sufficient liquidity—which are ideal for statistical trading strategies (e.g., Mean Reversion).

#### Key Logic (from `README.md`)
1.  **Hard Filter**: Average Daily Trading Value (20d) > **100억 KRW** (Filters out illiquid stocks).
2.  **Scoring (Tesla-Volatility Score, TVS)**:
    *   **40%** Daily Volatility & ATR Ratio (Short-term "Noise")
    *   **30%** RSI Volatility (Oscillation/Bounce Power)
    *   **30%** Weekly Volatility (Medium-term Trend Power)

### 2. How to Run

#### Prerequisites
Ensure dependencies are installed:
```bash
pip install pykrx yfinance pandas numpy
```

#### Command
Run the screener from the repository root:

```bash
python tesla_like_stocks_in_kospi/run_screener.py
```

*   **Note**: It may take 5-10 minutes to scan all KOSPI stocks as it downloads daily OHLCV data for ~900 tickers.

### 3. Interpreting Results

The script outputs a Top 20 table sorted by **TVS (Total Score)**.

#### Example Output
```text
🏆 Top 20 Candidates (TVS Ranking)
================================================================================
 rank_tvs ticker              name   TVS daily_vol rsi_std weekly_vol
        1 00xxxx       Hanwha Aero  98.5    0.0312    8.50     0.0610
        2 TSLA   Tesla (Benchmark)  95.2    0.0251    9.08     0.0517
        3 00xxxx    Samsung Heavy   91.0    0.0280    7.20     0.0450
...
```

*   **rank_tvs**: The ranking based on the combined volatility score.
*   **Tesla (Benchmark)**:
    *   **TSLA** is automatically fetched and inserted into the ranking.
    *   If TSLA is ranked #1 or Top 5, it means "KOSPI is currently boring/stable compared to the global volatility king".
    *   If TSLA is lower (e.g., #15), it means "There are KOSPI stocks wilder than Tesla right now!".
*   **TVS**: Score out of 100 (Percentile-based). Higher is better for volatility strategies.

### 4. Troubleshooting
*   **"No results found"**: Usually means network issues or the market is extremely quiet (filtering out everyone? unlikely).
*   **Slow execution**: The first run takes time to download data if not cached (currently not caching to disk to ensure fresh data).

## [2026-02-01:22:20] Reporting Features Added

Integrated automated reporting capabilities into the screener workflow.

### Features
1.  **Markdown Report Generation**:
    - Uses `TeslaReportGenerator` to create comprehensive reports.
    - Includes execution summary, Tesla benchmark ranking, and Top 20 candidate table.
2.  **Wiki Publishing**:
    - Automatically publishes the generated report to the GitHub Wiki.
    - Page Title format: `KOSPI Tesla-like Stocks Candidates (YYYY-MM-DD)`.
3.  **Telegram Notification**:
    - Sends a summary message to the configured Telegram chat upon successful Wiki publication.
    - Message includes Top 1 candidate, Tesla's rank, and a direct link to the Wiki report.

### Logic Flow (`run_screener.py`)
1.  Run Screener -> Get Results.
2.  Generate Markdown Report.
3.  Publish to Wiki -> Get Public URL.
4.  Send Telegram Message with Public URL.

## [2026-02-01:22:23] Fix: Import Path Issue in run_screener.py

Fixed `ModuleNotFoundError` when running the script from the `tesla_like_stocks_in_kospi` subdirectory.

### Changes
- Added `sys.path.append` to `run_screener.py` to dynamically include the project root.

## [2026-02-01:22:30] Successful Real Data Run (Limited)

Executed `run_screener.py --limit 50` to verify end-to-end functionality.
- **Result**: 5 candidates passed the liquidity filter. Tesla ranked #5.
- **Wiki**: Successfully updated with real KOSPI data.

## [2026-02-01:22:38] Fix: Stock Name Mapping

Resolved issue where stock names appeared as ticker numbers.
- **Problem**: `pykrx` returned empty names for some tickers.
- **Fix**: Implemented caching in `market_fetcher.py` to capture names during Naver crawling.

## [2026-02-01:22:45] Refinement: Filters & Clean-up

Refined filtering logic based on user feedback.

### Changes
1.  **Liquidity**: Minimum Avg Daily Value increased to **1,000억** KRW.
2.  **Exclusions**: Excluded ETFs, ETNs, SPACs, and Preferred Stocks using name-based filtering.
3.  **Tesla Benchmark**: Fixed logic to ensure Tesla (USD) passes the KRW-based liquidity check.

### Verification (`--limit 100`)
- **Filtered**: 1120 common stocks identified.
- **Result**: ETFs/ETNs excluded. Heavyweights like 'Hyundai Glovis' found.
- **Tesla**: Ranked #9.

