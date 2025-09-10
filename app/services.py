import httpx
import json
from typing import List
from .schemas import ConversationTurn, SummaryResponse, TaggingResponse, EmotionResponse
from core.config import settings
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

print(">>> loading services.py")

# --- Hugging Face Sentiment Analysis Model ---

class SentimentAnalyzer:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        self.model_name = model_name
        self.pipeline = None  # 지연 로딩을 위해 아직 로딩 안함

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

sentiment_analyzer = SentimentAnalyzer()

# --- End of Hugging Face Model ---

def _format_conversation(conversation: List[ConversationTurn]) -> str:
    """Formats a list of conversation turns into a single string."""
    return "\n".join([f"{turn.speaker}: {turn.text}" for turn in conversation])

async def _call_ollama(prompt: str) -> str:
    """Helper function to call the Ollama API and get the response."""
    api_url = f"{settings.OLLAMA_API_URL}/api/generate"
    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(api_url, json=payload)
            response.raise_for_status()

            response_text = response.text
            last_line = response_text.strip().split('\n')[-1]
            response_data = json.loads(last_line)
            
            if response_data.get("error"):
                error_message = response_data.get("error", "Unknown Ollama error")
                return f"LLM 모델 처리 중 오류가 발생했습니다: {error_message}"

            return response_data.get("response", "").strip()
        
        except httpx.TimeoutException as e:
            return f"LLM 모델 응답 시간 초과: {e}"
        except httpx.RequestError as e:
            return f"Ollama API 요청 중 오류 발생: {e}"
        except json.JSONDecodeError as e:
            return f"Ollama 응답 JSON 파싱 오류: {e}"
        except Exception as e:
            return f"알 수 없는 오류 발생: {e}"

async def summarize_text(request: List[ConversationTurn]) -> SummaryResponse:
    """Generates a summary for the given conversation using the LLM."""
    full_text = _format_conversation(request)
    prompt = f"다음 상담 내용을 세 문장으로 요약해줘.\n\n---\n{full_text}\n---"
    
    summary = await _call_ollama(prompt)
    
    return SummaryResponse(summary=summary)

async def tag_keywords(request: List[ConversationTurn]) -> TaggingResponse:
    """Extracts keywords from the given conversation using the LLM with a few-shot prompt."""
    full_text = _format_conversation(request)
    
    # Few-shot prompt to guide the model for better format compliance
    prompt = f'''You are a bot that extracts only the core keywords from a given text. Follow the output format exactly.

### Example
Input: 안녕하세요, 자동차 보험 갱신 때문에 전화했습니다. 보험료가 얼마나 나올지 궁금하고, 추가적으로 할인받을 수 있는 방법이 있는지도 알려주세요.
Output: 자동차 보험, 보험료, 갱신, 할인

### Task
Input: {full_text}
Output:'''
    
    keyword_string = await _call_ollama(prompt)
    
    tags = [tag.strip() for tag in keyword_string.split(',') if tag.strip()]
    
    return TaggingResponse(tags=tags)

async def analyze_emotion(request: List[ConversationTurn]) -> EmotionResponse:
    """Analyzes the emotion of the given conversation using the Hugging Face model."""
    full_text = _format_conversation(request)
    emotion = sentiment_analyzer.analyze(full_text)
    return EmotionResponse(emotion=emotion)