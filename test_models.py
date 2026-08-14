import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

print("사용 가능한 Gemini 모델:")

for model in client.models.list():
    if "generateContent" in str(model.supported_actions):
        print(model.name)