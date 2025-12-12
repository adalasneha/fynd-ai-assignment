import os
import requests
import streamlit as st

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"

def get_api_key():
    # 1️⃣ Streamlit Cloud
    if "OPENROUTER_API_KEY" in st.secrets:
        return st.secrets["OPENROUTER_API_KEY"]

    # 2️⃣ Local development (.env or system env)
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key

    raise RuntimeError(
        "OPENROUTER_API_KEY not found. "
        "Add it to Streamlit Secrets or environment variables."
    )

def call_llm(prompt: str) -> str:
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 200
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=40
    )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]
