# LLM 서버

이 서버는 대규모 언어 모델(LLM)을 사용하여 상담 텍스트에 대한 요약 및 키워드 태깅을 포함한 AI 기반 분석을 제공합니다.

## 디렉토리 구조

```
LLM_server/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI 앱 초기화 및 라우터 설정
│   ├── schemas.py      # 데이터 유효성 검증을 위한 Pydantic 모델
│   ├── services.py     # 핵심 비즈니스 로직 (예: LLM 호출)
│   └── api/
│       ├── __init__.py
│       └── endpoints/
│           ├── __init__.py
│           ├── summary.py    # 상담 요약 API
│           └── tagging.py    # 키워드 태깅 API
├── core/
│   ├── __init__.py
│   └── config.py       # 설정 관리 (예: API 키)
├── tests/
│   ├── __init__.py
│   └── test_api.py     # API 테스트 코드
├── .env                # 환경 변수 파일 (예: API 키)
├── requirements.txt    # 프로젝트 의존성
└── README.md           # 이 파일
```

## 디렉토리 및 파일 설명

*   **`app/`**: FastAPI 애플리케이션의 핵심 코드를 포함합니다.
    *   `main.py`: FastAPI 앱을 생성하고 라우터를 포함하며 애플리케이션의 진입점 역할을 합니다.
    *   `schemas.py`: API 요청 및 응답의 데이터 형식을 정의합니다 (예: `SummaryRequest`, `TaggingResponse`).
    *   `services.py`: LLM과 통신하여 요약 및 태깅을 수행하는 함수를 포함합니다.
    *   `api/endpoints/`: 기능별로 분리된 API 엔드포인트를 관리합니다.
        *   `summary.py`: 상담 요약 API 엔드포인트를 정의합니다.
        *   `tagging.py`: 키워드 태깅 API 엔드포인트를 정의합니다.
*   **`core/`**: 프로젝트의 핵심 설정 파일을 관리합니다.
    *   `config.py`: 외부 API 키 및 데이터베이스 정보와 같은 중요한 설정 값을 관리합니다.
*   **`tests/`**: 테스트 코드를 저장합니다.
*   **`.env`**: Git에 포함되어서는 안 되는 민감한 정보(API 키 등)를 저장합니다.
*   **`requirements.txt`**: `pip install -r requirements.txt`를 사용하여 한 번에 설치할 수 있는 필수 라이브러리 목록입니다.
*   **`README.md`**: 프로젝트에 대한 설명과 설치 및 실행 지침을 제공합니다.

이 구조를 통해 더 많은 기능이 개발될 때 `endpoints` 디렉토리에 새 파일을 추가하여 쉽게 확장할 수 있습니다.

## 설치 및 실행

1.  **`LLM_server` 디렉토리로 이동:**

    ```bash
    cd LLM_server
    ```

2.  **(권장) 가상 환경 생성 및 활성화:**

    ```bash
    # 가상 환경 생성
    python -m venv venv

    # Windows에서 활성화
    .\venv\Scripts\activate
    ```

3.  **필요한 라이브러리 설치:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **FastAPI 서버 실행:**

    ```bash
    uvicorn app.main:app --reload
    ```

서버가 성공적으로 실행되면, 터미널에 `http://127.0.0.1:8000` 주소에서 애플리케이션이 실행 중이라는 메시지가 나타납니다.

웹 브라우저에서 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 로 접속하면 자동으로 생성된 API 문서를 확인할 수 있으며, 여기에서 직접 API를 테스트해볼 수 있습니다.
