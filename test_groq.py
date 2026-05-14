import os
from dotenv import load_dotenv

# ── Test 1: Load .env ────────────────────────────────────
print("=" * 50)
print("TEST 1 — Loading .env file")
load_dotenv()
key = os.getenv("GROQ_API_KEY")
print(f"Key found: {key is not None}")
print(f"Key value: '{key}'")
print(f"Key length: {len(key) if key else 0}")
print(f"Starts with gsk_: {key.startswith('gsk_') if key else False}")

# ── Test 2: Direct API call ───────────────────────────────
print("\nTEST 2 — Direct API call")
import requests

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "say hello"}],
    "max_tokens": 10
}

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers=headers,
    json=payload
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

# ── Test 3: Using Groq library ────────────────────────────
print("\nTEST 3 — Using Groq library")
try:
    from groq import Groq
    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "say hello"}],
        max_tokens=10
    )
    print(f"✅ SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: {e}")