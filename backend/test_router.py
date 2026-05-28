import requests
import json

def test_router():
    print("Checking Research Endpoint with a non-finance query...")
    payload = {
        "query": "Write me a recipe for chocolate chip cookies",
        "company_symbol": "NONE"
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
    test_router()
