
from .schemas import AnalysisRequest, SummaryResponse, TaggingResponse

def summarize_text(request: AnalysisRequest) -> SummaryResponse:
    # In a real application, you would call an LLM here.
    # For now, we'll return a dummy summary.
    dummy_summary = f"요약 완료: {request.text[:30]}..."
    return SummaryResponse(summary=dummy_summary)

def tag_keywords(request: AnalysisRequest) -> TaggingResponse:
    # In a real application, you would call an LLM here.
    # For now, we'll return dummy tags.
    dummy_tags = ["상담", "키워드", "테스트"]
    return TaggingResponse(tags=dummy_tags)
