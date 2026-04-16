import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    BASE_URL = "https://openrouter.ai/api/v1"

    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



settings = Settings()
