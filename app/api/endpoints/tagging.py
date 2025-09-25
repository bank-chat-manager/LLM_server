from fastapi import APIRouter, Body
from typing import List

from app.schemas import ConversationTurn, TaggingResponse
from app.services import tag_keywords

router = APIRouter()

@router.post("/tagging", tags=["Tagging"])
async def post_tagging(request: List[ConversationTurn] = Body(...)) -> TaggingResponse:
    return await tag_keywords(request)
