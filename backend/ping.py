import requests
try:
    print("Pinging backend health endpoint...")
    res = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=5)
    print(res.status_code, res.text)
except Exception as e:
    print(f"Error: {e}")
