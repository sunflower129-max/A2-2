# 국내 여행 추천 프로그램

## 1. 프로그램 개요

사용자가 여행 날짜를 CLI로 입력하면 Google Gemini API와 Kakao Local API를 활용하여 국내 여행지를 추천하고 맛집을 검색한 후 최종 여행 리포트를 생성하는 Python CLI 프로그램입니다.

프로그램의 전체 흐름은 다음과 같습니다.

1. 사용자가 여행 날짜를 `YYYY-MM-DD` 형식으로 입력합니다.
2. Gemini API에 여행지 추천을 요청합니다.
3. Gemini의 응답을 JSON으로 파싱하여 구조화합니다.
4. 1차 추천 결과의 `recommended_city`를 Kakao Local API의 검색어로 사용합니다.
5. 추천 지역의 맛집을 최대 5곳 검색합니다.
6. 1차 여행 추천 결과와 맛집 검색 결과를 JSON 파일로 저장합니다.
7. Gemini API를 이용하여 최종 여행 리포트를 Markdown으로 생성합니다.
8. 최종 여행 리포트를 `results/` 폴더에 저장합니다.

---

## 2. 개발 환경

- Python 3.10 이상
- Google Gemini API
- Kakao Local API
- `argparse`
- `requests`
- `python-dotenv`
- `google-genai`

---

## 3. 프로젝트 구조

```text
국내여행추천/
├── .venv/
├── results/
│   ├── travel_YYYY-MM-DD.json
│   └── travel_report_YYYY-MM-DD.md
├── .env
├── .gitignore
├── main.py
├── requirements.txt
├── test_api.py
├── test_gemini.py
├── test_kakao.py
├── test_models.py
└── README.md
```

> `.env`에는 실제 API 키가 들어갈 수 있으므로 GitHub에 업로드하지 않습니다.

---

## 4. 실행 방법

### 4-1. 가상환경 활성화

Windows PowerShell에서 프로젝트 폴더로 이동한 후 가상환경을 활성화합니다.

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4-2. 필요한 패키지 설치

```powershell
pip install -r requirements.txt
```

`requirements.txt`에는 다음 패키지가 필요합니다.

```text
google-genai
requests
python-dotenv
```

### 4-3. 프로그램 실행

`-date` 옵션은 필수이며 `YYYY-MM-DD` 형식으로 입력합니다.

```powershell
python main.py -date "2026-09-20"
```

### 4-4. 날짜 형식이 잘못된 경우

```powershell
python main.py -date "20260920"
```

날짜 형식이 올바르지 않으면 다음과 같이 사용법을 안내하고 종료합니다.

```text
날짜 형식이 올바르지 않습니다.
사용법: python main.py -date "YYYY-MM-DD"
```

---

## 5. API 키 설정 방법

API 키는 Python 코드에 직접 작성하지 않고 `.env` 파일의 환경변수로 관리합니다.

프로젝트 최상위 폴더에 `.env` 파일을 만들고 다음 형식으로 설정합니다.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
KAKAO_API_KEY=YOUR_KAKAO_REST_API_KEY
```

Kakao 키는 프로그램에서 `KAKAO_API_KEY` 또는 `KAKAO_REST_API_KEY` 환경변수로 읽을 수 있습니다.

> 위의 `YOUR_...` 값은 설정 방법을 설명하기 위한 예시입니다. 실제 API 키를 README에 작성하지 않습니다.

---

## 6. API 키 보안 주의사항

- API 키를 Python 코드에 직접 작성하지 않습니다.
- `README.md`에 실제 API 키를 작성하지 않습니다.
- `.env` 파일을 GitHub에 업로드하지 않습니다.
- API 키가 포함된 화면을 제출용 캡처에 포함하지 않습니다.
- GitHub에 업로드하기 전에 `.gitignore`에 `.env`가 포함되어 있는지 확인합니다.
- API 키가 외부에 공개되었다면 해당 키를 폐기하거나 재발급합니다.

현재 `.gitignore`에는 다음과 같이 `.env`가 제외되어 있어야 합니다.

```text
.venv/
.env
__pycache__/
*.pyc
```

---

## 7. 주요 기능

### 7-1. CLI 인터페이스

`argparse`를 사용하여 다음과 같이 실행합니다.

```powershell
python main.py -date "YYYY-MM-DD"
```

`-date` 옵션은 필수입니다.

### 7-2. Gemini 1차 여행지 추천

입력한 날짜를 Gemini에 전달하고 다음 JSON 구조를 요구합니다.

```json
{
  "recommended_city": "추천 도시",
  "weather": "해당 시기의 일반적인 날씨 요약",
  "events": [
    "행사 또는 축제 후보 1",
    "행사 또는 축제 후보 2"
  ],
  "reason": "추천 근거를 2~4문장으로 작성"
}
```

필수 키는 `recommended_city`, `weather`, `events`, `reason`입니다.

Gemini 응답이 JSON으로 파싱되지 않는 경우 JSON 형식으로 다시 요청하여 최대 1회 재시도합니다.

### 7-3. Kakao Local 맛집 검색

Gemini의 `recommended_city`를 다음 단계의 입력으로 사용합니다.

검색어는 다음과 같이 구성됩니다.

```text
추천도시 + "맛집"
```

검색 결과에서 다음 정보를 확보합니다.

- 맛집 이름
- 주소
- 카테고리
- URL
- X 좌표
- Y 좌표

최대 5개의 맛집을 사용합니다.

### 7-4. 최종 여행 리포트 생성

Gemini의 1차 추천 JSON과 Kakao 맛집 검색 결과를 다시 Gemini에 전달하여 Markdown 여행 리포트를 생성합니다.

최종 리포트에는 다음 항목이 포함됩니다.

1. 추천 지역
2. 추천 이유
3. 날씨 요약
4. 행사/축제
5. 추천 맛집
6. 1일 여행 일정
7. 여행 팁

맛집 검색 결과가 없는 경우에도 리포트 생성을 계속하며 맛집 항목은 `데이터 없음`으로 처리할 수 있습니다.

---

## 8. 결과물 확인 방법

프로그램 실행이 완료되면 `results/` 폴더에 다음 파일이 생성됩니다.

### 8-1. 원본 데이터 JSON

```text
results/travel_YYYY-MM-DD.json
```

JSON에는 다음 정보가 포함됩니다.

```json
{
  "date": "YYYY-MM-DD",
  "recommendation": {},
  "restaurants": [],
  "errors": []
}
```

- `recommendation`: Gemini 1차 여행 추천 결과
- `restaurants`: Kakao 맛집 검색 결과
- `errors`: 실행 중 발생한 오류 목록

### 8-2. 최종 여행 리포트 Markdown

```text
results/travel_report_YYYY-MM-DD.md
```

Markdown 파일에는 추천 지역, 추천 이유, 날씨, 행사/축제, 맛집, 1일 일정 및 여행 팁이 포함됩니다.

---

## 9. 오류 처리

### API 키 미설정

Gemini 또는 Kakao API 키가 설정되지 않은 경우 오류 메시지를 출력하고 프로그램을 종료합니다.

### Gemini API 오류

Gemini API 호출 또는 응답 처리 과정에서 예외가 발생하면 오류 내용을 출력하고 내부 `errors` 목록에 기록합니다.

### Gemini JSON 파싱 오류

1차 Gemini 응답을 JSON으로 파싱하지 못하면 JSON만 다시 출력하도록 프롬프트를 수정하여 최대 1회 재시도합니다.

### Kakao API 오류

네트워크, 인증, 쿼터 등의 오류가 발생하면 맛집 목록을 빈 배열로 처리하고 오류를 `errors`에 기록합니다. 이후 원본 JSON 저장 및 최종 리포트 생성은 계속 진행할 수 있도록 구성합니다.

### 맛집 검색 결과가 0건인 경우

맛집 검색 결과가 없어도 프로그램이 중단되지 않으며 빈 리스트를 저장하고 최종 리포트 생성을 계속합니다.

---

## 10. REST API 요청/응답 구조

REST API는 HTTP를 이용하여 외부 서버와 데이터를 주고받는 방식입니다.

### GET

서버의 데이터를 조회할 때 주로 사용합니다.

Kakao Local 검색 API는 장소 검색 요청을 보내고 JSON 형태의 검색 결과를 받을 수 있습니다.

### POST

서버에 데이터를 전달하거나 서버에서 특정 처리를 요청할 때 주로 사용합니다.

GET과 POST는 HTTP 메서드이며 요청 목적과 데이터 전달 방식이 다릅니다.

---

## 11. LLM 출력과 다음 단계 연결

이 프로그램의 핵심은 LLM의 출력을 JSON으로 구조화한 후 다음 API 요청의 입력으로 사용하는 것입니다.

```text
사용자 입력
    ↓
여행 날짜
    ↓
Gemini API
    ↓
1차 여행 추천 JSON
    ↓
recommended_city 추출
    ↓
Kakao Local API
    ↓
맛집 검색 결과
    ↓
1차 추천 JSON + 맛집 목록
    ↓
Gemini API
    ↓
최종 Markdown 여행 리포트
```

`recommended_city`가 Gemini 결과와 Kakao Local 검색을 연결하는 핵심 데이터입니다.

---

## 12. 외부 API 오류 대응 원칙

| 오류 유형 | 대응 원칙 |
|---|---|
| 인증 오류 | API 키 존재 여부, 키 값, 헤더 설정 확인 |
| 권한 오류 | API 사용 권한 및 서비스 활성화 상태 확인 |
| 쿼터 오류 | API 사용량 및 한도 확인 |
| 네트워크 오류 | 연결 상태와 요청 timeout 확인 |
| JSON 파싱 오류 | 응답 형식 확인 및 최대 1회 재시도 |
| 검색 결과 0건 | 빈 목록으로 처리하고 다음 단계 진행 |

---

## 13. 실행 결과 예시

```powershell
python main.py -date "2026-09-20"
```

실행 후 `results/` 폴더에 다음 파일이 생성됩니다.

```text
results/
├── travel_2026-09-20.json
└── travel_report_2026-09-20.md
```

원본 JSON에는 1차 추천 결과, 맛집 검색 결과 및 오류 목록이 포함되고, Markdown 파일에는 최종 여행 리포트가 저장됩니다.

---

## 14. 제출 전 확인 사항

- [ ] `main.py`가 정상 실행되는가?
- [ ] `-date "YYYY-MM-DD"` 형식으로 실행되는가?
- [ ] 날짜 형식이 잘못되었을 때 사용법을 출력하는가?
- [ ] Gemini 1차 추천 결과가 JSON으로 처리되는가?
- [ ] `recommended_city`가 Kakao 맛집 검색에 연결되는가?
- [ ] 맛집 검색 결과가 JSON에 저장되는가?
- [ ] `errors` 배열이 JSON에 포함되는가?
- [ ] 최종 여행 리포트 `.md` 파일이 생성되는가?
- [ ] `results/` 폴더에 결과 파일이 존재하는가?
- [ ] `README.md`가 프로젝트 최상위 폴더에 있는가?
- [ ] `.gitignore`에 `.env`가 포함되어 있는가?
- [ ] 실제 API 키가 코드에 작성되어 있지 않은가?
- [ ] 실제 API 키가 README나 결과 파일에 포함되어 있지 않은가?
- [ ] 실제 API 키가 GitHub에 업로드되지 않았는가?

---

## 15. 보안 관련 최종 주의사항

`.env` 파일에는 실제 API 키가 포함될 수 있으므로 GitHub에 저장하지 않습니다.

실제 API 키는 과제 제출물, README, GitHub 저장소, 화면 캡처 등에 포함하지 않습니다.

API 키를 코드에 직접 넣는 대신 환경변수 또는 `.env`를 사용하는 이유는 다음과 같습니다.

1. 협업 및 공유 과정에서 API 키가 공개되는 실수를 줄일 수 있습니다.
2. API 키를 교체할 때 코드를 수정하지 않아도 됩니다.
3. 과금 및 API 쿼터가 있는 서비스의 오용을 예방할 수 있습니다.
