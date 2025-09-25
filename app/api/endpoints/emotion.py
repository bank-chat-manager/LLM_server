from fastapi import APIRouter, Body
from typing import List

from app.schemas import ConversationTurn, EmotionResponse
from app.services import analyze_emotion

router = APIRouter()

@router.post("/emotion", tags=["Emotion"])
async def post_emotion(request: List[ConversationTurn] = Body(...)) -> EmotionResponse:
    return await analyze_emotion(request)
