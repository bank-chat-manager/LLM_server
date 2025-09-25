import asyncio
import sys

# Windows에서 ProactorEventLoop를 사용하도록 설정하여 "too many file descriptors" 오류 방지
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from app.api.endpoints import summary, tagging, emotion

app = FastAPI(title="LLM Service for Banking Consultation")

app.include_router(summary.router, prefix="/api", tags=["Summary"])
app.include_router(tagging.router, prefix="/api", tags=["Tagging"])
app.include_router(emotion.router, prefix="/api", tags=["Emotion"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the LLM service."}
