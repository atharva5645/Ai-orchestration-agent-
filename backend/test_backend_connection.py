import requests

print("Testing direct connection to backend...")
payload = {
    "query": "What is the recent news on AAPL?",
    "company_symbol": "AAPL"
}

try:
    print(f"Sending payload: {payload}")
    res = requests.post("http://127.0.0.1:8000/api/v1/research/", json=payload, timeout=30)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
