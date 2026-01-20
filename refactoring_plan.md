# Refactoring Plan: Multi-Bot Architecture

## Goal
Restructure the project to support multiple trading/research bots by extracting shared logic into `common_modules` and isolating bot-specific logic.

## Target Structure
```
stock_research_bot/
├── common_modules/           # [NEW] Shared components
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dart_fetcher.py   # Moved from deep_value/src/data
│   │   └── market_fetcher.py # Moved from deep_value/src/data
│   ├── llm/
│   │   ├── __init__.py
│   │   └── llm_client.py     # Moved from deep_value/src/llm
│   └── notification/
│       ├── __init__.py
│       └── telegram_bot.py   # Moved from deep_value/src/notification
├── deep_value_asset_stocks/  # Specific Bot
│   ├── main.py               # Entry point (Updated imports)
│   ├── requirements.txt      # Bot specific deps
│   └── src/
│       ├── logic/
│       │   └── screener.py   # Bot specific logic
│       └── llm/
│           └── prompts.py    # Bot specific prompts
├── .env                      # [MOVED] Centralized configuration at root
└── README.md
```

## Execution Steps

1.  **Create Directory Structure**:
    - Create `common_modules` and subdirectories (`data`, `llm`, `notification`).
    - Create `__init__.py` files for package recognition.

2.  **Move Files**:
    - Move `dart_fetcher.py`, `market_fetcher.py` to `common_modules/data/`.
    - Move `llm_client.py` to `common_modules/llm/`.
    - Move `telegram_bot.py` to `common_modules/notification/`.
    - Move `.env` from `deep_value_asset_stocks/` to `stock_research_bot/`.

3.  **Refactor Code**:
    - **`DartFetcher`**: Update `mock_data.json` loading path (since it moves or needs to find it relative to module). *Decision*: Keep `mock_data.json` in `common_modules/data/` if it's generic, or keep it in bot folder and pass path? -> For now, move `mock_data.json` to `common_modules/data/` as a shared mock resource.
    - **`deep_value_asset_stocks/main.py`**: Update `sys.path` to include `../` so `common_modules` can be imported. Update import statements.
    - **`screener.py`**: Update imports if it relies on types from fetchers (duck typing, so maybe fine, but need to ensure it works).

4.  **Update Configuration**:
    - Update `.env` loading in `main.py` and other modules to look for `.env` in the parent directory (or use `python-dotenv`'s `find_dotenv` which usually handles recursion, or specify path).

5.  **Verification**:
    - Run `deep_value_asset_stocks/main.py` to ensure it still works in Mock Mode.
