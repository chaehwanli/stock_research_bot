# Implementation Plan: Stock Research Bot

## Goal Description
Develop an automated stock research and screening bot that identifies undervalued companies based on strict quantitative criteria (PBR <= 0.2, 5-year consecutive profit, high cash reserves, high insider ownership) and uses an LLM to generate a structured analyst report. The system will avoid subjective analysis and rely purely on data.

## System Architecture

### 1. Data Collection Bot
Responsible for fetching raw financial and market data.
- **DART (Open DART API)**:
    - `fnlttSinglAcntAll`: Get financial statements (Assets, Liabilities, Cash, Revenue, Operating Income).
    - `majorstock`: Get major shareholder information.
- **KRX / Naver Finance (via pykrx or finance-datareader)**:
    - Get daily OHLCV (for Market Cap).
    - Get PBR (or calculate using PBR = Market Cap / Net Assets).
- **Metadata**:
    - Identify Conglomerate groups (exclude).
    - Identify Managed/Suspended stocks (exclude).

### 2. Screening Engine (Python/Pandas)
Apply filtering logic before sending to LLM (to save tokens and ensure accuracy).
- **Filter 1 (PBR)**: Filter PBR <= 0.2 based on latest data.
- **Filter 2 (Profit)**: Check `Operating Income` > 0 for `2021, 2022, 2023, 2024, 2025` (or latest 5 available years).
- **Filter 3 (Cash)**: Calculate `(Cash & Equivalents + Short-term Financial Assets) / Total Assets`. Set a threshold (e.g., > 30% or significant vs Market Cap).
- **Filter 4 (Shareholding)**: Sum `Major Shareholder` + `Related Parties`. Check >= 50%.
- **Filter 5 (Exclusions)**: Remove if `Corp Group` (Conglomerate) or `Status` is Bad.

### 3. LLM Judgment Bot
Synthesize the collected data into the final report format and perform "Textual Judgment" if data is ambiguous.
- **Input**: JSON summary of the company's metrics.
- **Logic**: Verify conditions again (double-check), add "Validation" comments.
- **Output**: The requested structured text format.
- **Additional Task**: Check Net Cash, Dividend, Buyback status (if data available).

### 4. Notification Bot
- **Telegram**: Send the formatted message to a specific Chat ID.
- **CSV**: Save `results.csv` locally.

## Development Tasks

### Phase 1: Environment & Data Access
- [x] Set up Python project stricture.
- [x] Get Open DART API Key.
- [x] Implement `DartFetcher` class.
- [x] Implement `MarketDataFetcher` class.

### Phase 2: Logic Implementation
- [x] Implement `Screener` class with the 5 filters.
- [x] Create strict validation rules (Handle missing data as "Junk/False").

### Phase 3: LLM Integration
- [x] Setup LLM Client (OpenAI/Gemini).
- [x] Create Prompt Template for "Condition Confirmation & Report Generation".

### Phase 4: Pipeline & Notification
- [x] Build `main.py` pipeline.
- [x] Add Telegram notification.
- [x] Run full test on KOSPI/KOSDAQ.

## User Review Required
- **API Keys**: User needs to provide Open DART API Key and LLM API Key.
- **Thresholds**: Confirm the "High Cash" specific numerical threshold (e.g., 30%?). Defaulting to 30% for now.
