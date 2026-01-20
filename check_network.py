import requests

try:
    response = requests.get("https://www.google.com", timeout=5)
    print(f"Google Status Code: {response.status_code}")
except Exception as e:
    print(f"Google Connection Error: {e}")

try:
    response = requests.get("https://finance.naver.com", timeout=5)
    print(f"Naver Finance Status Code: {response.status_code}")
except Exception as e:
    print(f"Naver Finance Connection Error: {e}")
