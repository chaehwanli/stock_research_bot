import os
import json
import pandas as pd
import OpenDartReader

class DartFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.mock_data = None
        if self.api_key == "MOCK":
            self.load_mock_data()
        else:
            try:
                self.dart = OpenDartReader(api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenDartReader with provided key ({e}). Switching to MOCK mode.")
                self.api_key = "MOCK"
                self.load_mock_data()

    def load_mock_data(self):
        # mock_data.json is expected to be in the same directory as this file (common_modules/data)
        mock_path = os.path.join(os.path.dirname(__file__), "mock_data.json")
        try:
            with open(mock_path, "r", encoding="utf-8") as f:
                self.mock_data = json.load(f)
            print("Loaded mock data.")
        except Exception as e:
            print(f"Failed to load mock data: {e}")
            self.mock_data = {}

    def get_financial_summary(self, corp_code, year, reprt_code='11011'):
        if self.api_key == "MOCK":
            return self._get_mock_financials(corp_code, year)
        
        try:
            fs = self.dart.finstate_all(corp_code, year, reprt_code=reprt_code, fs_div='CFS')
            if fs is None:
                fs = self.dart.finstate_all(corp_code, year, reprt_code=reprt_code, fs_div='OFS')
            return fs
        except Exception as e:
            print(f"Error fetching financial summary: {e}")
            return None

    def _get_mock_financials(self, corp_code, year):
        if corp_code not in self.mock_data:
            return None
        
        data = self.mock_data[corp_code]["financials"].get(str(year))
        if not data:
            return None
        
        # Convert simple dict to DataFrame structure similar to DART output
        # This is a simplified mock; real DART returns multiple rows
        rows = []
        mapping = {
            "assets": "자산총계",
            "liabilities": "부채총계",
            "equity": "자본총계",
            "revenue": "매출액",
            "operating_income": "영업이익",
            "net_income": "당기순이익",
            "cash_and_equivalents": "현금및현금성자산",
            "short_term_financial_assets": "단기금융상품"
        }
        
        for k, v in data.items():
            if k in mapping:
                rows.append({
                    "account_nm": mapping[k],
                    "thstrm_amount": str(v), # DART returns strings
                    "thstrm_add_amount": "", # Simplified
                })
        
        return pd.DataFrame(rows)

    def get_major_shareholders(self, corp_code):
        if self.api_key == "MOCK":
            return self._get_mock_shareholders(corp_code)

        try:
            return self.dart.major_shareholders(corp_code)
        except Exception as e:
            print(f"Error fetching shareholders: {e}")
            return None

    def _get_mock_shareholders(self, corp_code):
        if corp_code not in self.mock_data:
            return None
        
        data = self.mock_data[corp_code].get("shareholders", [])
        return pd.DataFrame(data)

    def find_corp_code(self, corp_name):
        if self.api_key == "MOCK":
            for code, info in self.mock_data.items():
                if info["corp_name"] == corp_name:
                    return code
            return None

        try:
            return self.dart.find_corp_code(corp_name)
        except:
            return None
