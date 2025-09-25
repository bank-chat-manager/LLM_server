import asyncio
import sys
from fastapi import FastAPI

# 분리된 라우터들을 임포트합니다.
from app.api.endpoints import summary, tagging, emotion, reports

# Windows 이벤트 루프 정책 설정
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(
    title="LLM Service for Banking Consultation (Async with Celery)",
)

# 각 라우터를 애플리케이션에 포함시킵니다.
app.include_router(summary.router, prefix="/api")
app.include_router(tagging.router, prefix="/api")
app.include_router(emotion.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    """Health check endpoint."""
    return {"message": "Welcome to the LLM service (Async with Celery)."}
