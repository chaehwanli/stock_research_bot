# undervalued_bluechip_stock_research_bot
저평가 우량주 기업을 자동으로 탐색·선별하기 위한 LLM 기반 리서치/스크리닝 봇

**저평가 우량주 평가 점수표**는 기업의 재무 건전성(PER, PBR), 수익의 지속성, 그리고 미래 성장 잠재력을 종합적으로 점수화하여 저평가 우량주 기업으로 선정하고 투자 여부를 결정하는 방식

이 점수표는 4천만 원으로 시작해 55억 자산가가 된 투자자의 핵심 전략으로, **재무 상태 확인**을 첫 번째 단계로 강조합니다.

### 1. 저평가 우량주 평가 항목 및 배점
주요 평가는 이익 창출력, 저평가 여부, 지속 가능성, 그리고 기업 경쟁력을 기준으로 이루어집니다.

#### **재무 및 정량적 지표**
| 항목 | 구분 및 배점 |
| --- | --- |
| **PER (주가수익비율)** | **<5 (20점)** / <8 (15점) / <10 (10점) / >10 (5점) |
| **PBR (주가순자산비율)** | **<0.3 (5점)** / <0.6 (4점) / <1.0 (3점) / >1.0 (0점) |
| **중복 상장 여부** | **단독 상장 (5점)** / 자회사·손자회사 중복 상장 (0점) |
| **세계적 브랜드 보유** | **있음 (5점)** / 없음 (0점) |

#### **정성적 및 성장성 지표**
| 항목 | 구분 및 배점 |
| --- | --- |
| **이익 지속 가능성** | **대체로 지속 가능 (5점)** / 불안정한 이익 창출력 (0점) |
| **미래 성장 잠재력** | **매우 높다 (10점)** / 높다 (7점) / 보통 (5점) / 낮다 (3점) |
| **기업 경영진** | **우수한 경영자 (10점)** / 전문 경영자 (5점) / 저조한 실적·오너 경영 (0점) |

* 소스에 따르면, 이 외에도 **배당 수익률**의 유지 여부와 최근 **자사주 매입 및 소각**이 있었는지도 함께 살펴보는 것이 중요합니다.

---

### 2. 점수별 투자 등급 및 행동 지침
합산된 점수에 따라 투자 등급을 A~D로 나누며, **70점 이상**일 때 매수를 고려합니다.

*   **A등급 (80점 초과):** 장기 투자에 매우 적합하며 **적극 매수**를 권장합니다.
*   **B등급 (70점 ~ 80점):** 장기 투자에 적합하며 **매수**를 고려하는 단계입니다.
*   **C등급 (50점 ~ 70점 미만):** 추가 매수는 하지 않고 기존 투자를 유지(**홀딩**)합니다.
*   **D등급 (50점 미만):** 장기 투자를 추천하지 않으며 **매도**를 고려해야 합니다.

---

### 💡 투자 시 핵심 팁
*   **지속성 확인:** 단순히 현재 지표가 좋은 것뿐만 아니라, 배당이 지난 몇 년간 꾸준히 유지되었는지 확인해야 합니다.
*   **단순함의 원칙:** 자산가는 투자 비법이 거창한 것이 아니라, 이러한 기준으로 찾은 **저평가 우량주를 계속 사모으는 것**이라고 조언합니다.

---

# Implementation Plan: Undervalued Bluechip Stock Bot

## Goal
Create a research/screening bot that automatically identifies "Undervalued Bluechip Stocks" (저평가 우량주) based on a specific scoring system, targeting a total score of 70+ (Grade A/B).

## Scoring Criteria & Data Mapping

| Category | Item | Criteria (Points) | Data Source | Implementation |
|---|---|---|---|---|
| **Quant** | **PER** | <5 (20), <8 (15), <10 (10), >10 (5) | KIS/Naver (MarketDataFetcher) | `market.get_fundamental(ticker)['PER']` |
| **Quant** | **PBR** | <0.3 (5), <0.6 (4), <1.0 (3), >1.0 (0) | KIS/Naver (MarketDataFetcher) | `market.get_fundamental(ticker)['PBR']` |
| **Qual** | **Duplicate Listing** | Single (5), Duplicate (0) | LLM / DART | Ask LLM: "Is {name} a holding company or subsidiary with overlapping listed parent/child?" |
| **Qual** | **Global Brand** | Yes (5), No (0) | LLM | Ask LLM: "Does {name} have strong global brand recognition?" |
| **Hybrid** | **Profit Sustainability** | Sustainable (5), Unstable (0) | DART (History) + LLM | 1. Check DART for 5-year Op Income > 0.<br>2. LLM evaluates business model stability. |
| **Qual** | **Future Growth** | Very High (10), High (7), Med (5), Low (3) | LLM | Ask LLM: "Assess future growth potential of {name} based on industry trends." |
| **Qual** | **Management** | Excellent (10), Pro (5), Poor (0) | LLM | Ask LLM: "Evaluate management quality/reputation of {name}." |

## Architecture

### 1. New Package: `undervalued_bluechip_stocks`
- `main.py`: Entry point.
- `src/screener_bluechip.py`: Core logic class `BluechipScreener`.

### 2. Screening Workflow
1.  **Level 1 Filter (Quant)**: Scan ALL market tickers.
    -   Filter: PER < 20 (Broad pass to allow 5 points) AND PBR < 1.5.
    -   *Optimization*: Scanning 2000 companies with LLM is too expensive. We filter first.
2.  **Level 2 Analysis (Qual/LLM)**: For survivors of L1:
    -   Fetch Financial History (DART).
    -   Call LLM with a specific "Scoring Prompt".
    -   Parse LLM response to extract scores for Qual items.
3.  **Scoring & Grading**:
    -   Calculate Total Score.
    -   Assign Grade (A: >80, B: 70-80, C: 50-70, D: <50).
4.  **Reporting**:
    -   Generate Markdown Report (using `ReportGenerator`).
    -   Publish to Wiki.
    -   notify Telegram.

## Proposed Changes

### [NEW] `undervalued_bluechip_stocks/src/prompts.py`
- Define `BLUECHIP_SCORING_PROMPT`: Instructions for LLM to evaluate the qualitative aspects and output JSON/Score.

### [NEW] `undervalued_bluechip_stocks/src/screener_bluechip.py`
- Class `BluechipScreener`:
  - `run_screening()`: Orchestrates L1 and L2 screening.
  - `evaluate_company(ticker)`: Runs the scoring logic.

### [NEW] `undervalued_bluechip_stocks/main.py`
- Initialize modules (`DartFetcher`, `MarketDataFetcher`, `LLMClient`, `WikiPublisher`).
- Run `BluechipScreener`.
- Report & Publish.

## Verification
1.  **Test Script**: Create `test_bluechip_scoring.py` to run the scorer on a known Bluechip (e.g., Samsung Electronics) and a known low-quality stock.
2.  **Verify Scores**: Check if scores align with expectations.
3.  **Verify Wiki**: Check if report is published under "Undervalued_Bluechip_Report_YYYY-MM-DD".

## 구현 가이드
저평가 우량주 평가 점수표 구축을 위한 항목별 필요 데이터와 API 및 LLM기반 리서치 매핑 테이블 작성
매핑되지 않는 항목에 대한 평가 방안 정리
점수 계산 로직 구현
결과를 WIKI에 게시하고, Telegram으로 알림을 보내는 로직 구현
