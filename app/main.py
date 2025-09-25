import asyncio
import sys
from contextlib import asynccontextmanager

# Windows에서 ProactorEventLoop를 사용하도록 설정하여 "too many file descriptors" 오류 방지
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from app.api.endpoints import summary, tagging, emotion
from app.services import batch_processor # 배치 프로세서 임포트

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시
    print("--- Starting services ---")
    batch_processor.start()
    yield
    # 애플리케이션 종료 시
    print("--- Stopping services ---")
    await batch_processor.stop()

app = FastAPI(
    title="LLM Service for Banking Consultation",
    lifespan=lifespan # 라이프스팬 핸들러 등록
)

app.include_router(summary.router, prefix="/api", tags=["Summary"])
app.include_router(tagging.router, prefix="/api", tags=["Tagging"])
app.include_router(emotion.router, prefix="/api", tags=["Emotion"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the LLM service."}
