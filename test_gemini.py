import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="2026년 9월에 국내 여행하기 좋은 도시 한 곳을 추천해줘."
    )

    print("Gemini API 연결 성공!")
    print("\n응답:")
    print(response.text)

except Exception as e:
    print("Gemini API 호출 실패")
    print(e)