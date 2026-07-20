import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

candidate_models = [
    'gemini-flash-latest',
    'gemini-pro-latest',
    'gemini-3.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.5-pro'
]

for m in candidate_models:
    print(f"Testing {m}...")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("hello")
        print(f"SUCCESS with {m}: {response.text.strip()}")
        break
    except Exception as e:
        print(f"Failed {m}: {e}")
