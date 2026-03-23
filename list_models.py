import os
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    import traceback
    traceback.print_exc()
