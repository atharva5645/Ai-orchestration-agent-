import requests
import json

def test_api():
    print("1. Checking Health Endpoint...")
    try:
        health_res = requests.get("http://127.0.0.1:8000/health")
        print(f"Status: {health_res.status_code}")
        print(f"Response: {health_res.json()}\n")
    except Exception as e:
        print(f"Failed to connect to health endpoint: {e}")
        return

    print("2. Checking Research Endpoint...")
    payload = {
        "query": "Apple financial report",
        "company_symbol": "AAPL"
    }
    
    try:
        research_res = requests.post("http://127.0.0.1:8000/api/v1/research/", json=payload)
        print(f"Status: {research_res.status_code}")
        
        # Pretty print the JSON response
        formatted_json = json.dumps(research_res.json(), indent=2)
        print(f"Response:\n{formatted_json}")
        
    except Exception as e:
        print(f"Failed to connect to research endpoint: {e}")

if __name__ == "__main__":
    test_api()
