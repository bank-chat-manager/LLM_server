from fastapi import APIRouter
from app.schemas import AnalysisRequest, EmotionResponse
from app.services import analyze_emotion

router = APIRouter()

print(">>> loading emotion.py")
@router.post("/emotion", response_model=EmotionResponse)
async def get_emotion(request: AnalysisRequest):
    return await analyze_emotion(request)
