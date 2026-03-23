import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key}")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction="Test system instruction"
    )
    res = model.generate_content("Hello")
    print(f"Model generated: {res.text}")
except Exception as e:
    import traceback
    traceback.print_exc()
