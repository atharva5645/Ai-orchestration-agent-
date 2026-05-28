import os
from dotenv import load_dotenv
import requests

load_dotenv(".env.dev")
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

try:
    models = response.json().get("models", [])
    print(f"Found {len(models)} models.")
    for m in models:
        print(f"- {m['name']} (GenerateContent: {'generateContent' in m.get('supportedGenerationMethods', [])})")
except Exception as e:
    print(f"Error: {response.text}")
