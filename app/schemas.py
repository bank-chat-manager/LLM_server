
from pydantic import BaseModel
from typing import List

class AnalysisRequest(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str

class TaggingResponse(BaseModel):
    tags: List[str]
