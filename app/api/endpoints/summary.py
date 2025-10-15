from fastapi import APIRouter
from app.schemas import Conversation, SummaryResponse
from app.services import summarize_text

router = APIRouter()

@router.post("/summary", response_model=SummaryResponse)
async def get_summary(request: Conversation):
    return await summarize_text(request)
