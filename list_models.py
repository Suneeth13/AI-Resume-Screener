import google.generativeai as genai # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models = genai.list_models()
for model in models:
    print(model.name)
