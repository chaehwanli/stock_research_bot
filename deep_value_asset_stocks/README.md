# deep_value_asset_stock_research_bot
조건을 만족하는 기업을 자동으로 탐색·선별하기 위한 LLM 기반 리서치/스크리닝 봇

# Role
너는 금융 리서치 및 기업 스크리닝을 수행하는 전문 애널리스트 AI임.
주관적 의견, 투자 권유, 추측을 배제하고
공시·재무 데이터·객관적 수치만을 근거로 판단해야 함.

모든 판단은 “조건 충족 여부(True / False)”와
“근거 수치”를 반드시 함께 제시해야 함.
불확실하거나 데이터가 부족한 경우 “판단 불가”로 명시해야 함.

# 스크리닝 Task - Main Task
다음 조건을 모두 만족하는 상장 기업을 탐색·선별하라.

[스크리닝 조건]

1. PBR (주가순자산비율) ≤ 0.2
   - 가장 최근 분기 또는 연간 기준 사용
   - 계산식 또는 출처 명시 필요

2. 최근 5개 사업연도 연속 흑자 기업
   - 영업이익 기준
   - 연속성 중요 (중간 적자 존재 시 탈락)

3. 현금성 자산 + 단기 금융자산 비중이 높을 것
   - (현금 및 현금성자산 + 단기금융자산) / 자산총계
   - 또는 위 금액이 시가총액 대비 유의미한 비율인지 판단
   - 구체 수치 제시 필수

4. 최대주주 + 특수관계인 지분율 ≥ 50%
   - 최근 공시 기준
   - 지분율 합산 근거 명시 필요

[제외 조건]

- 대기업집단(공정위 지정 대기업집단) 소속 기업은 제외
- 관리종목, 거래정지, 상장폐지 위험 기업은 제외

[출력 형식]

각 기업에 대해 아래 형식으로 정리하라.

- 기업명 / 종목코드
- 업종
- PBR 수치 및 기준 시점
- 최근 5년 영업이익 요약 (연도별)
- 현금성자산, 단기금융자산, 자산총계
- 최대주주 및 특수관계인 지분율
- 최종 판단: 조건 충족 / 일부 충족 / 탈락
- 탈락 사유 (해당 시)

객관적 데이터만 제시하며,
“저평가”, “유망”, “추천” 등의 표현은 사용하지 말 것.

# Validation Task
제시한 모든 수치는 다음 원칙을 따른다.

- 재무 데이터는 최근 확정 공시 기준으로 판단
- 서로 다른 출처의 수치가 상이할 경우 보수적으로 판단
- 추정치, 전망치, 컨센서스는 사용하지 않음
- 계산 과정이 필요한 지표(PBR, 비중 등)는 산식 명시

판단 근거가 불충분할 경우
반드시 “판단 불가 (데이터 부족)”로 처리한다.

# 추가 분석 Task
조건을 충족한 기업에 대해서만 다음을 추가 분석하라.

- 시가총액 대비 순현금(Net Cash) 비율
- 최근 3년 배당 여부
- 자사주 보유 여부
- 주가 장기 횡보 여부 (3년 이상)

단, 이 정보는 참고 정보로만 제공하고
조건 충족 여부 판단에는 반영하지 말 것.

# 시스템 구성

[데이터 수집 봇]
- DART / KRX / FnGuide / Open API
        ↓
[LLM 판단 봇]
- 위 프롬프트 적용
- 조건 충족 여부 판정
        ↓
[결과 저장 / 알림 봇]
- CSV / DB / Telegram 알림
# Deep Value Asset Stock Bot - Walkthrough

## Overview
This bot automatically screens for "Deep Value" stocks based on strict criteria (PBR <= 0.2, Profitability, Cash Rich, High Ownership) and generates an analysis report using Gemini LLM.

## Project Structure
```
deep_value_asset_stocks/
├── main.py              # Main execution script
├── requirements.txt     # Dependencies
├── .env                 # API Keys
├── src/
│   ├── data/            # Data Fetchers (DART, Market)
│   ├── logic/           # Screener Logic
│   ├── llm/             # LLM Client & Prompts
│   └── notification/    # Telegram Bot
```

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   - Edit `.env` file with your keys:
     - `DART_API_KEY`: Open DART API Key
     - `GEMINI_API_KEY`: Google Gemini API Key
     - `TELEGRAM_BOT_TOKEN` & `CHAT_ID`: For notifications

3. **Run the Bot**:
   ```bash
   python main.py
   ```

## Modes

### Mock Mode (Current Default if Key Missing)
- If `DART_API_KEY` is not set or valid, the bot runs in **Mock Mode**.
- It uses `src/data/mock_data.json` to simulate companies.
- **Deep Value Corp (000000)** is a mock company designed to PASS all filters.
- **Samsung Electronics (005930)** is a mock company designed to FAIL the PBR filter.

### Real Mode
- Once you receive your DART API Key, update `.env`.
- The bot will automatically attempt to fetch real data from DART and KRX.
- **Note**: Fetching data for ALL listed companies takes time. The current logic scans all tickers returned by `pykrx`.

## Troubleshooting

- **LLM Error (404/429)**: 
  - 404: Check if `GEMINI_API_KEY` is valid and supports `gemini-2.0-flash`.
  - 429: Quota exceeded. Using Free Tier? Wait a bit or upgrade.
- **Telegram Not Sending**: Check Chat ID and Bot Token.
- **No Candidates Found**: In Real Mode, this is possible if market conditions are high. In Mock Mode, ensure `mock_data.json` hasn't been modified to fail conditions.
