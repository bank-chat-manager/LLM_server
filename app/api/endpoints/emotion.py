from fastapi import APIRouter
from typing import List
from app.schemas import ConversationTurn, EmotionResponse
from app.services import analyze_emotion

router = APIRouter()

@router.post("/emotion", response_model=EmotionResponse)
async def get_emotion(request: List[ConversationTurn]):
    return await analyze_emotion(request)