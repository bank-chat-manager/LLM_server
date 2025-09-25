from typing import List
from .schemas import ConversationTurn, SummaryResponse, TaggingResponse, EmotionResponse
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

print(">>> loading services.py")

# --- Hugging Face Sentiment Analysis Model ---

class SentimentAnalyzer:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        self.model_name = model_name
        self.pipeline = None  # 지연 로딩

    def _load_model(self):
        if self.pipeline is None:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

    def analyze(self, text: str) -> str:
        self._load_model()
        result = self._pipeline(text)[0]
        label = result['label']
        
        # Convert star rating to sentiment
        star = int(label.split()[0])
        if star <= 2:
            return "부정"
        elif star == 3:
            return "중립"
        else:
            return "긍정"

# --- Service Instantiation ---
sentiment_analyzer = SentimentAnalyzer()

# --- Service Functions (to be updated for Celery) ---

async def summarize_text(request: List[ConversationTurn]) -> SummaryResponse:
    """(This function will be updated to call the Celery task)"""
    # This will be replaced by a call to summarize_task.delay()
    return SummaryResponse(summary="Processing... a task ID will be returned here.")

async def tag_keywords(request: List[ConversationTurn]) -> TaggingResponse:
    """(This function will be updated to call a Celery task)"""
    # This can be updated later to use Celery as well
    return TaggingResponse(tags=["tagging", "will", "be", "implemented"])

async def analyze_emotion(request: List[ConversationTurn]) -> EmotionResponse:
    """Analyzes the emotion of the given conversation using the Hugging Face model."""
    full_text = "\n".join([f"{turn.speaker}: {turn.text}" for turn in request])
    emotion = sentiment_analyzer.analyze(full_text)
    return EmotionResponse(emotion=emotion)
