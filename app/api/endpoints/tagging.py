from fastapi import APIRouter
from typing import List
from app.schemas import ConversationTurn, TaggingResponse
from app.services import tag_keywords

router = APIRouter()

@router.post("/tagging", response_model=TaggingResponse)
async def get_tags(request: List[ConversationTurn]):
    return await tag_keywords(request)