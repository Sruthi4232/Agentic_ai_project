import os
from openai import OpenAI

# Try both .env and manual entry
key = os.getenv("OPENAI_API_KEY", "").strip() or "sk-YOUR-REAL-KEY-HERE"
print(f"Testing key: {key[:10]}...")

client = OpenAI(api_key=key)

try:
    models = client.models.list()
    print("✅ API key is valid! You can access:", len(models.data), "models.")
except Exception as e:
    print("❌ API key error:", e)
