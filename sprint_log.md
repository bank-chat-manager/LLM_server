## Sprint Log: LLM 서버 초기 구축

**날짜:** 2025년 8월 30일

### 1. FastAPI 프로젝트 구조 설정

- **`main.py`**: FastAPI 애플리케이션의 메인 진입점 설정. 요약 및 태깅 API 라우터를 포함.
- **`schemas.py`**: API 요청 및 응답 데이터의 형식을 정의하는 Pydantic 모델 작성.
  - `AnalysisRequest`: 입력 텍스트를 받는 모델
  - `SummaryResponse`: 요약 결과를 반환하는 모델
  - `TaggingResponse`: 키워드 태그 리스트를 반환하는 모델
- **`api/endpoints/`**: 기능별 라우터 분리.
  - `summary.py`: `/summary` 엔드포인트 생성.
  - `tagging.py`: `/tagging` 엔드포인트 생성.
- **`requirements.txt`**: `fastapi`, `uvicorn`, `python-dotenv`, `httpx` 등 프로젝트 의존성 명시.

### 2. LLM 연동을 위한 설정 및 서비스 구현

- **`core/config.py`**: 외부 서비스(Ollama)의 설정을 관리하기 위한 파일 생성.
  - `pydantic-settings`를 사용하여 `OLLAMA_API_URL`을 환경 변수 또는 기본값으로 관리하도록 설정.
- **`app/services.py`**: 핵심 비즈니스 로직 구현.
  - 기존의 더미(dummy) 함수를 실제 LLM을 호출하는 코드로 교체.
  - `httpx.AsyncClient`를 사용하여 Ollama API (`/api/generate`)에 비동기 POST 요청을 보내도록 구현.
  - **요약 프롬프트**: "다음 상담 내용을 세 문장으로 요약해줘."
  - **키워드 태깅 프롬프트**: "다음 상담 내용의 핵심 키워드를 5개만 쉼표(,)로 구분해서 알려줘. 다른 설명은 붙이지마."
  - API 응답에서 순수 텍스트 결과를 추출하고, 키워드의 경우 쉼표로 분리하여 리스트로 변환하는 로직 추가.

### 3. 비동기(Asynchronous) 처리 적용

- `app/services.py`의 `summarize_text`, `tag_keywords` 함수를 `async def`로 변경.
- `api/endpoints/summary.py`와 `api/endpoints/tagging.py`의 엔드포인트 함수들을 `async def`로 수정하고, 서비스 함수 호출 시 `await` 키워드를 사용하여 비동기 I/O를 올바르게 처리하도록 변경.

### 4. 문서화

- **`README.md`**: 프로젝트 구조, 설치 및 실행 방법, 로컬 LLM 도구(Ollama, LM Studio 등) 비교/선정 과정, 그리고 최종 모델(`gemma:2b`) 선정 과정 및 전략을 상세히 기록.

### 5. 트러블슈팅

- **`ModuleNotFoundError: pydantic_settings`**
  - **원인**: `core/config.py`에서 `pydantic-settings` 라이브러리를 사용했으나, `requirements.txt`에 추가하는 것을 누락함.
  - **해결**: `requirements.txt`에 `pydantic-settings`를 추가하고 `pip install -r requirements.txt`를 통해 의존성을 재설치함.

- **긴 텍스트 입력 시 `422 Unprocessable Content` 오류**
  - **초기 가설**: 텍스트 내 특수 문자로 인한 JSON 형식 오류로 추정.
  - **디버깅 과정**:
    1.  Ollama API 호출부를 더미 데이터로 교체했을 때 정상 작동 → API 연동 과정의 문제로 범위 축소.
    2.  `summary.py`에서 Pydantic 자동 검증을 우회하고 `request.json()`을 수동 호출 → `json.decoder.JSONDecodeError` 발생 확인.
  - **최종 원인**: FastAPI의 `/docs` 테스트 UI가 긴 텍스트의 줄바꿈 문자를 제대로 이스케이프(escape) 처리하지 못해, 서버로 깨진 형식의 JSON 요청을 보냈기 때문.
  - **해결**: `curl`과 `@payload.json` 파일을 사용하여, 올바른 형식의 요청을 터미널에서 직접 전송하는 것으로 우회하여 테스트 성공.

- **PowerShell 환경에서 `curl` 명령어 오류**
  - **원인**: PowerShell은 `@` 문자를 'Splatting' 연산자로 해석하므로, 파일 내용을 읽는 `-d @payload.json` 구문이 실패함.
  - **해결**: PowerShell의 `Get-Content` 명령어를 사용하는 `curl -d (Get-Content -Raw payload.json)` 구문으로 수정하여 해결.

- **`gemma:2b` 모델의 키워드 추출 실패**
  - **문제**: "쉼표로 구분된 키워드"라는 지시사항을 모델이 따르지 않고, 요약과 유사한 문장 형태의 결과를 반환함.
  - **시도**: Few-shot 프롬프팅(예시 제공)을 통해 원하는 결과물의 형식을 명시적으로 알려주었으나, 모델이 여전히 프롬프트의 예시 부분만 참고하고 실제 과업은 무시하는 등 혼란을 보임.
  - **결론**: `gemma:2b` 모델의 지시 사항 준수 능력(Instruction Following)의 명확한 한계로 판단.

## Next Sprint 목표

- **모델 교체 및 성능 테스트**: `gemma:2b`의 키워드 추출 성능 한계를 확인했으므로, 더 지시를 잘 따르는 `phi-3-mini` 모델로 교체하고 요약 및 키워드 추출 성능을 재평가.