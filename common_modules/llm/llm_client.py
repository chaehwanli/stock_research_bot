import os
import time
from google import genai
from dotenv import load_dotenv

# Load .env from project root (2 levels up from common_modules/llm/llm_client.py)
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(env_path)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in .env")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-3-pro-preview'

    def _call_with_retry(self, func, *args, **kwargs):
        """
        Retries the function call if it fails with a 429 error.
        Max retries: 4. Initial delay: 15s.
        """
        max_retries = 4
        delay = 15 
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if attempt < max_retries:
                        print(f"LLM 429 Limit hit. Waiting {delay}s before retry ({attempt+1}/{max_retries})...")
                        time.sleep(delay)
                        delay *= 2 # Exponential backoff
                        continue
                raise e # Re-raise if not 429 or max retries exceeded

    def analyze_company(self, company_data, prompt_template):
        """
        Sends company data to LLM for analysis using the provided prompt.
        """
        if not self.client:
            return "Error: No API Key or Client not initialized"

        prompt = prompt_template.format(
            name=company_data['name'],
            ticker=company_data['ticker'],
            pbr=company_data['pbr'],
            profit_history=company_data['profit_history'],
            cash_ratio=f"{company_data['cash_ratio']:.2%}",
            shareholder_stake=f"{company_data['shareholder_stake']}%"
        )
        
        try:
            # New SDK usage: client.models.generate_content
            response = self._call_with_retry(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error calling LLM: {e}"

    def generate_text(self, prompt):
        """
        Generic method to send any text prompt to the LLM.
        """
        if not self.client:
            return "Error: Client not initialized"
            
        try:
            response = self._call_with_retry(
                self.client.models.generate_content,
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error calling LLM: {e}"
