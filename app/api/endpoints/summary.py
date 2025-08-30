
from fastapi import APIRouter
from app.schemas import AnalysisRequest, SummaryResponse
from app.services import summarize_text

router = APIRouter()

@router.post("/summary", response_model=SummaryResponse)
def get_summary(request: AnalysisRequest):
    return summarize_text(request)
