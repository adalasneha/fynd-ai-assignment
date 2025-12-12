import os
import requests
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found. Add it to .env")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"   # You can change the model later

def call_llm(prompt):
    """Send a simple prompt to OpenRouter and return only the text output."""
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 200
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=40)
    response.raise_for_status()
    data = response.json()

    # Extract return text
    return data["choices"][0]["message"]["content"]
