# 🌍 AI 기반 여행 플래너 CLI 프로그램

사용자가 입력한 날짜(`-date`)를 기반으로 LLM(Gemini 또는 OpenAI)이 여행 도시, 날씨, 행사 정보를 추천하고, 지도 API(Kakao Local 또는 Naver Local)를 통해 해당 도시의 맛집 정보를 수집한 뒤 최종 **Markdown 여행 리포트**를 생성해주는 CLI Python 프로그램입니다.

---

## 📦 1. 프로그램 개요 및 주요 기능

1. **LLM 연동 (날씨/행사 추천)**: 입력된 날짜를 분석하여 추천 도시, 날씨 요약, 주요 행사 및 추천 근거를 **구조화된 JSON** 형태로 생성합니다.
2. **지도/장소 API 연동 (맛집 검색)**: 1차 추천 결과로 나온 도시를 바탕으로 맛집 5곳을 검색합니다. (검색 실패 시에도 프로그램이 중단되지 않고 "데이터 없음"으로 처리됩니다.)
3. **최종 리포트 생성**: 수집된 모든 데이터를 바탕으로 깔끔한 Markdown 형식의 여행 일정 리포트를 `results/` 폴더에 자동 저장합니다.
4. **안정적인 에러 처리**: API 키 미설정 시 즉시 안내 후 종료, JSON 파싱 실패 시 최대 1회 재시도, 지도 API 실패 시에도 리포트 생성을 지속하는 방어적 로직이 적용되어 있습니다.

---

## ⚙️ 2. API 키 설정 방법 (보안 주의)

이 프로그램은 보안을 위해 **API 키를 코드에 직접 작성하지 않고 환경변수(.env)**로 관리합니다.

1. 프로젝트 루트 폴더에 `.env` 파일을 생성합니다.
2. 아래 템플릿을 참고하여 본인의 API 키를 입력합니다.

### `.env` 파일 예시
```env
# Google Gemini API 사용 시 (택 1)
GOOGLE_API_KEY="AIzaSyYourActualKeyHere"

# 또는 OpenAI API 사용 시 (택 1)
OPENAI_API_KEY="sk-YourActualKeyHere"

# Kakao Local API 사용 시 (택 1)
KAKAO_API_KEY="YourKakaoRestApiKeyHere"

# 또는 Naver Local Search API 사용 시 (택 1)
NAVER_CLIENT_ID="YourNaverClientIdHere"
NAVER_CLIENT_SECRET="YourNaverClientSecretHere"

# ✈️ 국내 여행 추천 CLI 프로그램 (AI Travel Planner)

본 프로젝트는 입력된 날짜(`YYYY-MM-DD`)를 바탕으로 **Google Gemini API**를 활용해 최적의 국내 여행지를 추천받고, **Kakao Local Search API**를 연동하여 해당 지역 맛집 정보를 수집한 뒤, 최종 여행 리포트(`Markdown`)와 원본 데이터(`JSON`)를 자동으로 생성하는 CLI 파이프라인 프로그램입니다.

---

## 📌 주요 기능
- **CLI 날짜 입력 검증**: `argparse`를 활용해 `-date "YYYY-MM-DD"` 형태의 날짜 입력을 검증합니다.
- **Gemini 1차 여행지 추천**: 지정된 날짜의 일반적인 날씨, 추천 행사/축제, 추천 이유를 JSON 형식으로 응답받습니다. (파싱 실패 시 1회 재시도 로직 포함)
- **Kakao Local 맛집 검색**: 1차 추천 도시를 기반으로 Kakao Local API에서 맛집 5곳을 수집합니다.
- **오류 예외 처리 & Fallback**: API Key 미설정 시 즉시 종료 안내, Kakao API 장애 시 맛집 데이터를 빈 값으로 처리하여 리포트 생성을 계속 진행하며, 모든 에러 로그는 JSON에 기록됩니다.
- **결과 저장**: `results/` 폴더 내에 원본 JSON(`travel_YYYY-MM-DD.json`)과 Markdown 리포트(`travel_report_YYYY-MM-DD.md`)를 저장합니다.

---

## 📂 프로젝트 구조

```text
.
├── main.py                    # 여행 추천 메인 실행 스크립트
├── results/                   # 실행 결과물 저장 폴더 (자동 생성)
│   ├── travel_2026-10-15.json # 원본 데이터 (추천 결과 + 맛집 + 에러 로그)
│   └── travel_report_2026-10-15.md # 최종 Markdown 여행 리포트
├── .env                       # API Key 설정 파일 (Git 관리 제외)
├── .env.example               # 환경변수 설정 템플릿
├── .gitignore                 # Git 관리 제외 목록
├── requirements.txt           # 의존성 패키지 목록
└── README.md                  # 프로젝트 설명서