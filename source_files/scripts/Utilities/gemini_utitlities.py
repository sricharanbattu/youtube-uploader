import os
import google.genai as genai

def getGeminiApiKey():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in your environment first")
    
    return api_key



