from fastapi import APIRouter
from app.schemas import Conversation, EmotionResponse
from app.services import analyze_emotion

router = APIRouter()

@router.post("/emotion", response_model=EmotionResponse)
async def get_emotion(request: Conversation):
    return await analyze_emotion(request)