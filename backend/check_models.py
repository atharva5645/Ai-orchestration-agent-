import requests

response = requests.get("https://openrouter.ai/api/v1/models")
models = response.json().get("data", [])

gemini_models = [m["id"] for m in models if "gemini" in m["id"].lower() and "flash" in m["id"].lower()]
print("Available Gemini Flash Models on OpenRouter:")
for m in gemini_models:
    print(m)
