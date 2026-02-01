import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common_modules.llm.llm_client import LLMClient

def test_llm():
    print("Initializing LLMClient...")
    llm = LLMClient()
    
    if not llm.client:
        print("ERROR: LLMClient failed to initialize (client is None). Check .env and API Key.")
        return

    print(f"API Key loaded? {bool(llm.api_key)}")
    if llm.api_key:
        print(f"API Key start: {llm.api_key[:5]}...")
    
    print("Testing generation...")
    try:
        response = llm.generate_text("Hello, are you working? Reply with 'Yes'.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"ERROR calling generate_text: {e}")

if __name__ == "__main__":
    test_llm()
