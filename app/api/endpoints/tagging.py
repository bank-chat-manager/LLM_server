from fastapi import APIRouter
from app.schemas import AnalysisRequest, TaggingResponse
from app.services import tag_keywords

router = APIRouter()

@router.post("/tagging", response_model=TaggingResponse)
async def get_tags(request: AnalysisRequest):
    return await tag_keywords(request)
