from pydantic import BaseModel
from typing import List

# A single turn in the conversation
class ConversationTurn(BaseModel):
    speaker: str
    text: str

# The request body will be a list of these turns: List[ConversationTurn]

class SummaryResponse(BaseModel):
    summary: str

class TaggingResponse(BaseModel):
    tags: List[str]

class EmotionResponse(BaseModel):
    emotion: str