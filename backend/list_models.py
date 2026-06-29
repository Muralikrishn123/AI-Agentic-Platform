"""List available Gemini models for your API key."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No API key found")
    exit(1)

print("🔍 Listing available Gemini models...")
print("=" * 80)

genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    
    print("\n✅ Available models:\n")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  • {model.name}")
            print(f"    Display name: {model.display_name}")
            print(f"    Description: {model.description[:80]}...")
            print()
    
except Exception as e:
    print(f"❌ Error: {e}")
