import os
import requests
from dotenv import load_dotenv

load_dotenv()

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

url = "https://dapi.kakao.com/v2/local/search/keyword.json"

headers = {
    "Authorization": f"KakaoAK {KAKAO_API_KEY}"
}

params = {
    "query": "제주 맛집",
    "size": 3
}

try:
    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    print("HTTP 상태 코드:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("\nKakao API 연결 성공!")
        print("검색 결과:")

        for place in data["documents"]:
            print(
                f"- {place['place_name']} | "
                f"{place['address_name']}"
            )

    else:
        print("Kakao API 호출 실패")
        print(response.text)

except requests.RequestException as e:
    print("네트워크 오류:", e)