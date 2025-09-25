from fastapi import APIRouter
from typing import List
from app.schemas import ConversationTurn, SummaryResponse
from app.services import summarize_text

router = APIRouter()

@router.post("/summary", response_model=SummaryResponse)
def get_summary(request: List[ConversationTurn]):
    return summarize_text(request)
