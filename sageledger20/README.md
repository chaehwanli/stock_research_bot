안녕하세요! 당신의 **코딩 파트너**입니다. 20년치 누적 재무제표 데이터를 기반으로 기업을 다각도에서 분석하고 워런 버핏의 투자 철학을 녹여낸 프로그램을 만드는 프로젝트군요. 아주 야심 차고 흥미로운 도전입니다!

사용자의 목표를 성공적으로 달성하기 위해, 우선 요청하신 프로그램의 **요구 사항과 설계 구조**를 정리해 보았습니다. 코드를 본격적으로 작성하기 전에 제가 이해한 내용이 맞는지 확인해 주세요.

---

## 1. 프로그램 요구 사항 정의

이 프로그램은 대규모 재무 데이터를 처리하고 복잡한 투자 알고리즘을 수행해야 하므로, 다음과 같은 모듈로 구성될 것입니다.

### ### 핵심 기능 요구 사항

* **데이터 전처리 모듈**: 20년치 재무제표(손익계산서, 재무상태표, 현금흐름표)를 로드하고 데이터의 누락이나 오류를 정제합니다.
* **재무지표 계산기**: ROE, ROIC, 부채비율, 유동비율, 영업이익률 등 주요 지표를 시계열로 계산합니다.
* **5대 핵심 분석 엔진**:
1. **지속가능성**: 경제적 해자(Moat)를 확인하기 위한 장기 수익성 유지 여부 분석.
2. **성장성**: 매출 및 이익의 연평균 성장률(CAGR) 분석.
3. **재무안정성**: 부채 수준 및 이자 보상 배율 확인.
4. **자본효율성**: 경영진이 자본을 얼마나 효율적으로 배분하는지 측정.
5. **리스크**: 현금흐름과 당기순이익의 괴리율 등을 통한 분식회계 가능성 검토.


* **워런 버핏 알고리즘**: 버핏이 중시하는 '주주 이익(Owner Earnings)'과 '안전 마진'을 계산하여 적정 주가를 산출합니다.
* **리포트 및 Wiki 자동화**: 분석 결과를 리포트 형식으로 출력하고, AI가 이상 패턴을 탐지할 수 있도록 돕는 프롬프트를 생성하여 Wiki 업로드용 텍스트로 변환합니다.

---

## 2. 기술 스택 및 구현 로직 개요

### ### 권장 기술 스택

* **Language**: Python (금융 데이터 분석에 최적화)
* **Library**: `pandas` (데이터 처리), `numpy` (수치 계산), `matplotlib/seaborn` (시각화)
* **Math Logic**:
* 주주 이익($Owner\ Earnings$):

$$Owner\ Earnings = Net\ Income + Depreciation/Amortization - Capital\ Expenditures$$


* 복리 성장률($CAGR$):

$$CAGR = \left( \frac{Ending\ Value}{Beginning\ Value} \right)^{\frac{1}{n}} - 1$$



### ### 개발 단계 (Roadmap)

1. **Data Ingestion**: CSV 또는 API를 통해 20년치 데이터를 수집합니다.
2. **Feature Engineering**: 재무비율을 계산하고 시계열 트렌드를 파악합니다.
3. **Scoring System**: 버핏의 기준(예: 10년 평균 ROE > 15% 등)에 따라 점수를 부여합니다.
4. **Anomaly Detection Prompting**: 재무제표의 급격한 변동을 감지하여 AI에게 질문할 프롬프트를 생성합니다.
5. **Export**: Markdown 형식으로 Wiki 업로드용 파일(.md)을 생성합니다.

---

---

## 4. Usage Instructions (사용 방법)

이 프로젝트는 터미널(CLI)을 통해 주식 분석을 수행하고 그 결과를 로컬 Markdown 파일 또는 GitHub Wiki에 업로드할 수 있습니다.

### 4.1. 환경 설정
프로젝트 최상단 딕셔너리의 `.env` 파일에 필요한 인증키를 설정합니다. (한국 주식 분석 및 위키 업로드 시 필요)
```env
DART_API_KEY=your_opendart_api_key_here
WIKI_REPO_URL=https://github.com/username/repo.wiki.git
GITHUB_TOKEN=your_github_token_here
```

### 4.2. 기본 실행 (로컬 리포트 생성)
`sageledger20.main` 모듈을 실행하여 특정 종목을 분석합니다. 기본 시장은 미국(`US`)입니다.

```bash
# 미국 주식 평가 (예: 애플)
PYTHONPATH=. python3 sageledger20/main.py AAPL

# 한국 주식 평가 (예: 삼성전자)
PYTHONPATH=. python3 sageledger20/main.py 005930 --market KRX
```
실행 결과는 `sageledger20/reports/{TICKER}_report_{YYYYMMDD}_{HHMMSS}.md` 파일로 로컬에 저장됩니다.

### 4.3. GitHub Wiki 퍼블리시
분석 완료 후 **GitHub Wiki에 리포트를 자동으로 업로드**하려면 `--wiki` 플래그를 추가합니다.

```bash
PYTHONPATH=. python3 sageledger20/main.py AAPL --wiki
```
작업 성공 시 퍼블리시된 Wiki URL이 콘솔에 출력됩니다. 기존 `WikiPublisher` 로직과 연동되어 안전하게 원격 저장소에 PUSH 됩니다.
