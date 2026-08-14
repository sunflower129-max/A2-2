import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
kakao_key = os.getenv("KAKAO_API_KEY")

print("Gemini API 키:", "설정됨" if gemini_key else "없음")
print("Kakao API 키:", "설정됨" if kakao_key else "없음")