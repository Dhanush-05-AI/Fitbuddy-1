import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
print("Key found in .env:", bool(key))
print("Model:", model)
print("Key length:", len(key) if key else 0)
print("Starts with:", key[:5] if key else None)
print("Repr of last 3 chars:", repr(key[-3:]) if key else None)

client = genai.Client(api_key=key)
response = client.models.generate_content(model=model, contents="Say hello in five words.")
print("Gemini replied:", response.text)