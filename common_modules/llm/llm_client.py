import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env from project root (2 levels up from common_modules/llm/llm_client.py)
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(env_path)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in .env")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def analyze_company(self, company_data, prompt_template):
        """
        Sends company data to LLM for analysis using the provided prompt.
        """
        if not self.api_key:
            return "Error: No API Key"

        prompt = prompt_template.format(
            name=company_data['name'],
            ticker=company_data['ticker'],
            pbr=company_data['pbr'],
            profit_history=company_data['profit_history'],
            cash_ratio=f"{company_data['cash_ratio']:.2%}",
            shareholder_stake=f"{company_data['shareholder_stake']}%"
        )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error calling LLM: {e}"
