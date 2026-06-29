import app.patch
import google.generativeai as genai
from config.settings import settings
import traceback

print("Configuring API Key...")
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Testing Gemini generate...")
model = genai.GenerativeModel('gemini-2.5-flash')
try:
    model.generate_content("Hello")
    print("Success!")
except Exception as e:
    traceback.print_exc()
