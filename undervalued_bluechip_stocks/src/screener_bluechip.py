import json
import re
from .prompts import BLUECHIP_SCORING_PROMPT

class BluechipScreener:
    def __init__(self, dart_fetcher, market_fetcher, llm_client):
        self.dart = dart_fetcher
        self.market = market_fetcher
        self.llm = llm_client

    def run_screening(self, tickers):
        print(f"Starting Bluechip Screening for {len(tickers)} tickers...")
        candidates = []
        stats = {
            "scanned": len(tickers),
            "passed_quant": 0,
            "passed_final": 0
        }

        # 1. Level 1: Quant Filter
        quant_pass_tickers = []
        for ticker in tickers:
            if self._check_quant_criteria(ticker):
                quant_pass_tickers.append(ticker)
        
        stats["passed_quant"] = len(quant_pass_tickers)
        print(f"Passed Quant Filter: {len(quant_pass_tickers)} companies")

        # 2. Level 2: Qual Analysis via LLM
        # Limit to top 5 for testing/mock if list is huge
        if len(quant_pass_tickers) > 5 and self.market.use_mock:
             print("Mock Mode: Limiting to first 5 for speed.")
             quant_pass_tickers = quant_pass_tickers[:5]
        
        # Real mode limit to avoid huge API costs if too many pass? 
        # For now, let's process max 20.
        if len(quant_pass_tickers) > 20:
            print("Warning: Limiting L2 screening to 20 random survivors to check costs.")
            quant_pass_tickers = quant_pass_tickers[:20]

        for ticker in quant_pass_tickers:
            result = self.evaluate_company(ticker)
            if result:
                print(f"  -> {result['name']}: Total Score {result['total_score']} (Grade {result['grade']})")
                if result['grade'] in ['A', 'B']:
                    candidates.append(result)

        stats["passed_final"] = len(candidates)
        return candidates, stats

    def _check_quant_criteria(self, ticker):
        """
        Broad filter: PER < 20, PBR < 1.5
        """
        try:
            fund = self.market.get_fundamental(ticker)
            if fund is None or fund.empty: return False
            
            per = float(fund.get('PER', 100))
            pbr = float(fund.get('PBR', 100))
            
            # Simple broad filter
            if 0 < per < 20 and 0 < pbr < 1.5:
                return True
        except:
            return False
        return False

    def evaluate_company(self, ticker):
        corp_name = self.market.get_stock_name(ticker)
        print(f"Evaluating {corp_name} ({ticker})...")
        
        # 1. Fetch Data
        fund = self.market.get_fundamental(ticker)
        if fund is None or fund.empty: return None
        
        per = float(fund.get('PER', 0))
        pbr = float(fund.get('PBR', 0))
        
        # Calculate Quant Scores
        quant_reasoning = []
        score_per = 0
        if per < 5: score_per = 20
        elif per < 8: score_per = 15
        elif per < 10: score_per = 10
        else: score_per = 5 # anything >= 10
        quant_reasoning.append(f"PER {per} -> {score_per}pts")
        
        score_pbr = 0
        if pbr < 0.3: score_pbr = 5
        elif pbr < 0.6: score_pbr = 4
        elif pbr < 1.0: score_pbr = 3
        elif pbr <= 1.0: score_pbr = 3 # Handle potential rounding or exact 1.0
        else: score_pbr = 0
        quant_reasoning.append(f"PBR {pbr} -> {score_pbr}pts")
        
        # Get Financial History
        profit_history_str = "Data Not Available"
        # In real impl, we should fetch DART listing here.
        # For MVP, let's trust the LLM's internal knowledge or provide mock data if needed.
        if self.dart.api_key == "MOCK":
             profit_history_str = "2020: 100B, 2021: 120B, 2022: 150B, 2023: 130B, 2024: 160B"

        # 2. LLM Analysis
        company_data = {
            "name": corp_name,
            "ticker": ticker,
            "profit_history": profit_history_str,
            "pbr": pbr,
            "per": per
        }
        
        prompt = BLUECHIP_SCORING_PROMPT.format(**company_data)
        
        try:
            response_json_str = self.llm.generate_text(prompt)
            # Parse JSON
            # Cleanup markdown code blocks if present
            cleaned_json = response_json_str.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_json)
            
            qual_score = data.get("total_qual_score", 0)
            reasoning = data.get("reasoning", "")
            
            # Additional keys
            s_dup = data.get("duplicate_listing_score", 0)
            s_brand = data.get("global_brand_score", 0)
            s_prof = data.get("profit_sustainability_score", 0)
            s_grow = data.get("growth_potential_score", 0)
            s_mgmt = data.get("management_score", 0)
            
            total_score = score_per + score_pbr + qual_score
            
            # Grade
            if total_score > 80: grade = 'A'
            elif total_score >= 70: grade = 'B'
            elif total_score >= 50: grade = 'C'
            else: grade = 'D'
            
            return {
                "ticker": ticker,
                "name": corp_name,
                "score_per": score_per,
                "score_pbr": score_pbr,
                "score_qual": qual_score,
                "total_score": total_score,
                "grade": grade,
                "details": {
                    "per": per,
                    "pbr": pbr,
                    "duplicate_listing": s_dup,
                    "global_brand": s_brand,
                    "profit_sustainability": s_prof,
                    "growth_potential": s_grow,
                    "management": s_mgmt,
                    "llm_reasoning": reasoning
                }
            }

        except Exception as e:
            print(f"Error evaluating {corp_name}: {e}")
            return None
