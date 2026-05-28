import os
from dotenv import load_dotenv
import requests

def test_raw_gemini():
    load_dotenv(".env.dev")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("No GOOGLE_API_KEY found in .env.dev")
        return

    # Direct REST API call to Google bypassing LangChain completely
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{"parts":[{"text": "Say hello"}]}]
    }
    
    print("Testing direct Google REST API...")
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_raw_gemini()
