from pydantic import BaseModel
from typing import List, Dict

# The request body will be a list of dictionaries, where each dictionary maps a speaker to their text.
Conversation = List[Dict[str, str]]

class SummaryResponse(BaseModel):
    summary: str

class TaggingResponse(BaseModel):
    tags: List[str]

class EmotionResponse(BaseModel):
    emotion: str