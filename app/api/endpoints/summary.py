from fastapi import APIRouter, Request
from app.schemas import AnalysisRequest, SummaryResponse
from app.services import summarize_text

router = APIRouter()

print(">>> loading summary.py")
@router.post("/summary", response_model=SummaryResponse)
async def get_summary(request: Request):
    # Manually parse the JSON body to bypass automatic validation issues
    data = await request.json()
    analysis_request = AnalysisRequest(**data)
    return await summarize_text(analysis_request)