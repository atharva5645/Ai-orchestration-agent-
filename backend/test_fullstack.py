import requests
import time

print("--- Full Stack Integration Test ---")

# 1. Health check
print("\n[1] Health check...")
try:
    res = requests.get("http://127.0.0.1:8001/health/", timeout=5)
    print(f"    Status: {res.status_code} -> {res.json()}")
except Exception as e:
    print(f"    FAILED: {e}")
    exit(1)

# 2. Research query
print("\n[2] Sending research query...")
try:
    payload = {"query": "What is HDFC AMC silver ETF price today?", "company_symbol": ""}
    start = time.time()
    res = requests.post("http://127.0.0.1:8001/api/v1/research/", json=payload, timeout=180)
    elapsed = time.time() - start
    print(f"    Status: {res.status_code} | Took: {elapsed:.1f}s")
    data = res.json()
    print(f"    Pipeline Status: {data.get('status')}")
    if data.get("error"):
        print(f"    ERROR: {data['error']}")
    else:
        report = data.get("final_report", "")
        print(f"    Report length: {len(report)} chars")
        print(f"    Report preview:\n{'='*60}")
        print(report[:500])
        print("="*60)
except Exception as e:
    print(f"    FAILED: {e}")
