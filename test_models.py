import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
    "gemini-pro"
]

for m in models_to_test:
    try:
        print(f"Testing {m}...")
        model = genai.GenerativeModel(m)
        res = model.generate_content("Hello")
        print(f"[{m}] SUCCESS: {res.text[:20]}...")
    except Exception as e:
        print(f"[{m}] FAILED: {str(e)[:100]}")
