import argparse
import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from google import genai


# ==========================================
# 환경변수 불러오기
# ==========================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
KAKAO_API_KEY = (
    os.getenv("KAKAO_API_KEY")
    or os.getenv("KAKAO_REST_API_KEY")
)


# ==========================================
# Gemini 1차 여행지 추천
# ==========================================

def get_gemini_recommendation(travel_date):
    """Gemini에게 여행지 추천을 요청하고 JSON으로 반환"""

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY가 설정되지 않았습니다. "
            ".env 파일을 확인해주세요."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
당신은 국내 여행 추천 전문가입니다.

여행 날짜는 {travel_date}입니다.

해당 날짜에 국내에서 여행하기 좋은 도시 한 곳을 추천해주세요.

반드시 아래 JSON 형식으로만 답변하세요.
JSON 이외의 설명이나 마크다운은 작성하지 마세요.

{{
  "recommended_city": "추천 도시",
  "weather": "해당 시기의 일반적인 날씨 요약",
  "events": [
    "행사 또는 축제 후보 1",
    "행사 또는 축제 후보 2"
  ],
  "reason": "추천 근거를 2~4문장으로 작성"
}}

events는 1~3개의 문자열을 포함해야 합니다.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        data = json.loads(text)

    except json.JSONDecodeError:

        retry_prompt = f"""
이전 답변을 JSON으로 파싱할 수 없었습니다.

여행 날짜: {travel_date}

아래 4개 키만 포함하는 올바른 JSON만 출력하세요.

{{
  "recommended_city": "도시명",
  "weather": "날씨 요약",
  "events": ["행사 1", "행사 2"],
  "reason": "추천 이유"
}}

JSON 이외의 문자는 절대 출력하지 마세요.
"""

        retry_response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=retry_prompt
        )

        retry_text = retry_response.text.strip()

        if retry_text.startswith("```"):
            retry_text = retry_text.replace("```json", "")
            retry_text = retry_text.replace("```", "")
            retry_text = retry_text.strip()

        data = json.loads(retry_text)

    required_keys = [
        "recommended_city",
        "weather",
        "events",
        "reason"
    ]

    for key in required_keys:
        if key not in data:
            raise ValueError(
                f"Gemini 응답에 필수 키가 없습니다: {key}"
            )

    return data


# ==========================================
# Kakao 맛집 검색
# ==========================================

def search_kakao_restaurants(city):
    """추천 도시를 기준으로 Kakao Local에서 맛집 검색"""

    if not KAKAO_API_KEY:
        raise RuntimeError(
            "KAKAO_API_KEY가 설정되지 않았습니다. "
            ".env 파일을 확인해주세요."
        )

    url = (
        "https://dapi.kakao.com/v2/local/"
        "search/keyword.json"
    )

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    params = {
        "query": f"{city} 맛집",
        "size": 5
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    restaurants = []

    for item in data.get("documents", []):

        restaurant = {
            "name": item.get("place_name", ""),
            "address": item.get("address_name", ""),
            "category": item.get("category_name", ""),
            "url": item.get("place_url", ""),
            "x": (
                float(item["x"])
                if item.get("x")
                else None
            ),
            "y": (
                float(item["y"])
                if item.get("y")
                else None
            )
        }

        restaurants.append(restaurant)

    return restaurants


# ==========================================
# 결과 JSON 저장
# ==========================================

def save_json_result(
    travel_date,
    recommendation,
    restaurants,
    errors
):
    """여행 추천 결과를 JSON 파일로 저장"""

    results_dir = "results"

    os.makedirs(
        results_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        results_dir,
        f"travel_{travel_date}.json"
    )

    result_data = {
        "date": travel_date,
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors
    }

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return file_path


# ==========================================
# 메인 프로그램
# ==========================================
# ==========================================
# 최종 여행 리포트 생성
# ==========================================

def generate_travel_report(
    travel_date,
    recommendation,
    restaurants
):
    """Gemini를 이용해 최종 Markdown 여행 리포트를 생성"""

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY가 설정되지 않았습니다."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    restaurant_text = json.dumps(
        restaurants,
        ensure_ascii=False,
        indent=2
    )

    recommendation_text = json.dumps(
        recommendation,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
당신은 국내 여행 전문 작가입니다.

아래 여행 추천 JSON과 맛집 검색 결과를 바탕으로
{travel_date} 여행자를 위한 최종 여행 리포트를 작성하세요.

[1차 여행 추천 JSON]
{recommendation_text}

[맛집 검색 결과]
{restaurant_text}

반드시 Markdown 형식으로 작성하세요.

다음 항목을 반드시 포함하세요.

# 국내 여행 추천 리포트

## 1. 추천 지역
추천 지역과 추천 이유를 설명하세요.

## 2. 날씨 요약
제공된 날씨 정보를 바탕으로 설명하세요.

## 3. 행사/축제
제공된 행사 또는 축제 후보를 목록으로 정리하세요.

## 4. 추천 맛집
검색된 맛집을 번호가 있는 목록 또는 표로 정리하세요.
각 맛집의 이름, 주소, 카테고리를 포함하세요.

맛집이 없다면 "데이터 없음"이라고 작성하세요.

## 5. 1일 여행 일정
오전 / 오후 / 저녁으로 나누어 여행 일정을 제안하세요.

## 6. 여행 팁
여행자가 참고할 만한 간단한 팁을 작성하세요.

제공된 데이터에 없는 구체적인 사실은
확정된 사실처럼 만들지 마세요.

Markdown 본문만 출력하세요.
"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()


# ==========================================
# Markdown 리포트 저장
# ==========================================

def save_markdown_report(
    travel_date,
    report_text
):
    """최종 여행 리포트를 Markdown 파일로 저장"""

    results_dir = "results"

    os.makedirs(
        results_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        results_dir,
        f"travel_report_{travel_date}.md"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report_text)

    return file_path

def main():

    parser = argparse.ArgumentParser(
        description="국내 여행 추천 프로그램"
    )

    parser.add_argument(
        "-date",
        required=True,
        help="여행 날짜 (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    # 날짜 형식 검증
    try:
        travel_date = datetime.strptime(
            args.date,
            "%Y-%m-%d"
        )

    except ValueError:
        print("날짜 형식이 올바르지 않습니다.")
        print(
            '사용법: python main.py -date "YYYY-MM-DD"'
        )
        return

    # 오류 목록
    errors = []

    print("================================")
    print("국내 여행 추천 프로그램")
    print("================================")
    print(
        f"여행 날짜: "
        f"{travel_date.strftime('%Y-%m-%d')}"
    )
    print()

    # --------------------------------------
    # Gemini 1차 추천
    # --------------------------------------

    print(
        "Gemini에게 여행지 추천을 요청합니다..."
    )

    try:

        recommendation = get_gemini_recommendation(
            travel_date.strftime("%Y-%m-%d")
        )

        print()
        print("================================")
        print("1차 여행 추천 결과")
        print("================================")

        print(
            f"추천 도시: "
            f"{recommendation['recommended_city']}"
        )

        print(
            f"날씨: "
            f"{recommendation['weather']}"
        )

        print("행사/축제:")

        for event in recommendation["events"]:
            print(f"- {event}")

        print(
            f"추천 이유: "
            f"{recommendation['reason']}"
        )

    except Exception as e:

        print()
        print(
            "Gemini API 호출 또는 처리 중 "
            "오류가 발생했습니다."
        )

        print(e)

        errors.append(
            f"Gemini 오류: {str(e)}"
        )

        return

    # --------------------------------------
    # Kakao 맛집 검색
    # --------------------------------------

    print()
    print("================================")
    print("Kakao 맛집 검색")
    print("================================")

    recommended_city = (
        recommendation["recommended_city"]
    )

    print(
        f"검색 도시: {recommended_city}"
    )

    print(
        "추천 도시를 기준으로 "
        "맛집을 검색합니다..."
    )

    try:

        restaurants = search_kakao_restaurants(
            recommended_city
        )

        if restaurants:

            print(
                f"맛집 검색 결과: "
                f"{len(restaurants)}곳"
            )

            for index, restaurant in enumerate(
                restaurants,
                start=1
            ):

                print(
                    f"{index}. "
                    f"{restaurant['name']} - "
                    f"{restaurant['address']}"
                )

        else:

            restaurants = []

            print(
                "맛집 검색 결과가 없습니다."
            )

    except Exception as e:

        restaurants = []

        print(
            "Kakao 맛집 검색 중 "
            "오류가 발생했습니다."
        )

        print(e)

        errors.append(
            f"Kakao 오류: {str(e)}"
        )

    # --------------------------------------
    # 원본 JSON 저장
    # --------------------------------------

    json_path = save_json_result(
        travel_date.strftime("%Y-%m-%d"),
        recommendation,
        restaurants,
        errors
    )

    print()
    print("================================")
    print("원본 데이터 저장 완료")
    print("================================")
    print(
        f"저장 경로: {json_path}"
    )
    # --------------------------------------
    # 최종 Markdown 여행 리포트 생성
    # --------------------------------------

    print()
    print("================================")
    print("최종 여행 리포트 생성")
    print("================================")

    try:

        report_text = generate_travel_report(
            travel_date.strftime("%Y-%m-%d"),
            recommendation,
            restaurants
        )

        report_path = save_markdown_report(
            travel_date.strftime("%Y-%m-%d"),
            report_text
        )

        print(
            "최종 여행 리포트 생성 완료"
        )

        print(
            f"저장 경로: {report_path}"
        )

    except Exception as e:

        errors.append(
            f"리포트 생성 오류: {str(e)}"
        )

        print(
            "최종 리포트 생성 중 "
            "오류가 발생했습니다."
        )

        print(e)

# ==========================================
# 프로그램 시작
# ==========================================

if __name__ == "__main__":
    main()