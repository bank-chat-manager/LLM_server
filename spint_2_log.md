## Sprint Log: 감정 분석 API 기능 추가

**날짜:** 2025년 9월 10일

### 1. 목표
- 텍스트 감정 분석 모델을 AI 서버에 연결하고, 그 결과를 API로 반환하는 기능 구현

### 2. 개발 내용

- **`schemas.py` 수정**:
  - 감정 분석 결과를 담을 `EmotionResponse` Pydantic 모델 추가 (`{"emotion": "긍정"}`).

- **API 엔드포인트 추가 (`api/endpoints/emotion.py`)**:
  - `/api/emotion` 경로에 대한 새로운 FastAPI 라우터 생성.
  - 텍스트를 입력받아 감정 분석 결과를 JSON 형태로 반환.

- **의존성 추가 (`requirements.txt`)**:
  - 기존 Ollama 연동 방식에서 로컬 Hugging Face 모델 사용으로 변경.
  - `transformers`와 `torch` 라이브러리를 의존성에 추가.

- **서비스 로직 구현 (`services.py`)**:
  - Hugging Face의 `nlptown/bert-base-multilingual-uncased-sentiment` 모델을 사용하도록 `analyze_emotion` 함수 구현.
  - `SentimentAnalyzer` 클래스를 구현하여, 애플리케이션 시작 시 모델과 토크나이저를 한 번만 로드하도록 최적화.
  - 모델의 출력값(예: "5 stars")을 "긍정", "부정", "중립"의 세 가지 카테고리로 변환하는 로직 추가.

- **애플리케이션 라우터 연결 (`main.py`)**:
  - 생성된 `emotion` 라우터를 메인 FastAPI 앱에 포함.

- **테스트 코드 작성 (`tests/test_api.py`)**:
  - 기존 엔드포인트(`/`, `/api/summary`, `/api/tagging`)와 새로운 `/api/emotion` 엔드포인트에 대한 테스트 케이스 5개 작성.

### 3. 트러블슈팅

- **`pytest` 테스트 수집(collecting) 오류**:
  - **원인**: `tests/__init__.py` 파일로 인한 순환 참조 및 `sys.path` 문제.
  - **해결**: `tests/__init__.py` 파일을 삭제하고, `pytest.ini` 파일을 생성하여 프로젝트 루트 경로를 명시적으로 추가.

- **`transformers` 모델 로딩 오류**:
  - **원인**: `AutoModelForSequenceClassification` 클래스를 `from_pretrained` 메서드 없이 직접 인스턴스화하려고 시도.
  - **해결**: `AutoModelForSequenceClassification.from_pretrained("모델명")` 형태로 수정하여 정상적으로 모델을 로드.

- **`pipeline` 태스크 이름 오류**:
  - **원인**: `pipeline` 생성 시 `"sentiment_analysis"` (언더스코어)를 사용하여 `KeyError` 발생.
  - **해결**: 공식 문서에 명시된 대로 `"sentiment-analysis"` (하이픈)으로 수정하여 해결.

### 4. 최종 결과
- 상기 트러블슈팅 과정을 거쳐, 작성된 5개의 테스트 케이스가 모두 **성공적으로 통과**함을 확인.
- 목표했던 감정 분석 API 기능 구현 완료.

### Next Sprint 목표
- 다음 스프린트 목표 논의 필요.
