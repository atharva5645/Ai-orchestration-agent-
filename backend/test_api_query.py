import requests

try:
    print("Sending request to backend...")
    payload = {"query": "provide me hdfc silver price", "company_symbol": ""}
    res = requests.post("http://127.0.0.1:8000/api/v1/research/", json=payload, timeout=120)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Error: {e}")
