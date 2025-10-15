from fastapi import APIRouter
from app.schemas import Conversation, TaggingResponse
from app.services import tag_keywords

router = APIRouter()

@router.post("/tagging", response_model=TaggingResponse)
async def get_tags(request: Conversation):
    return await tag_keywords(request)