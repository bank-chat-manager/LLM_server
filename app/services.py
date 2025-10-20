import httpx
import json
import asyncio
from typing import List
from .schemas import Conversation, SummaryResponse, TaggingResponse, EmotionResponse
from core.config import settings
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

print(">>> loading services.py")

# --- Concurrency Control ---
llm_semaphore = asyncio.Semaphore(5)

# --- Batch Processing Settings ---
BATCH_SIZE = 16
BATCH_TIMEOUT = 0.1 # seconds

async def _call_ollama_batch(prompts: List[str]) -> List[str]:
    """Calls the Ollama API with a batch of prompts."""
    # Create a single prompt that instructs the LLM to process a batch
    combined_prompt = (
        "You are an AI assistant that processes requests in batches. "
        "Each request is a text to be summarized in three sentences. "
        "The requests are numbered. Provide the corresponding summarized output for each request, starting with 'OUTPUT 1:', 'OUTPUT 2:', etc., on new lines. "
        "Ensure there is one summarized output for each input request.\n\n"
    )

    for i, p in enumerate(prompts, 1):
        combined_prompt += f"--- INPUT {i} ---\n{p}\n\n"

    combined_prompt += "--- OUTPUTS ---"

    # Use the existing semaphore to limit concurrent BATCH requests
    async with llm_semaphore:
        # The actual API call logic is similar to the single-request version
        api_url = f"{settings.OLLAMA_API_URL}/api/generate"
        payload = {
            "model": "qwen2:0.5b",
            "prompt": combined_prompt,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client: # Increased timeout for batch
            try:
                response = await client.post(api_url, json=payload)
                response.raise_for_status()

                response_text = response.text
                last_line = response_text.strip().split('\n')[-1]
                response_data = json.loads(last_line)
                
                if response_data.get("error"):
                    # If the whole batch fails, return an error for each item
                    error_message = response_data.get("error", "Unknown Ollama error")
                    return [f"LLM 배치 처리 중 오류: {error_message}"] * len(prompts)

                raw_output = response_data.get("response", "").strip()
                
                # Parse the combined output back into individual summaries
                # Expected format: "OUTPUT 1: ... \nOUTPUT 2: ..."
                summaries = []
                # Split by "OUTPUT " and then find the number
                parts = raw_output.split(f"OUTPUT ")[1:] # The first part is empty
                
                # Create a dictionary to hold summaries by index
                summary_map = {}
                for part in parts:
                    try:
                        index_str, summary_text = part.split(":", 1)
                        index = int(index_str.strip())
                        summary_map[index] = summary_text.strip()
                    except ValueError:
                        continue # Ignore malformed parts

                # Fill summaries list, ensuring order and handling missing ones
                for i in range(1, len(prompts) + 1):
                    summaries.append(summary_map.get(i, "요약 결과 파싱 실패"))
                
                return summaries

            except Exception as e:
                # If the request itself fails, return an error for each item
                return [f"LLM 배치 API 호출 중 오류: {e}"] * len(prompts)

# --- Hugging Face Sentiment Analysis Model ---

class SentimentAnalyzer:
    """
    감정 분석 모델 클래스 정의
    """
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
        

class ConversationTagger:
    """
    태깅 모델 정의
    """
    def __init__(self, model_name="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"):
        self.model_name = model_name
        self.classifier = None
        self.candidate_labels = [
            '추천상품',
            '예금',
            '펀드',
            '대출',
            '외환',
            '골드',
            '신탁',
            '보험',
            '퇴직연금',
            'ISA'
        ]

    def _load_model(self):
        if self.classifier is None:
            self.classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
            print("태깅 모델 로딩 완료")
    
    def tagging(self, text:str) -> str:
        self._load_model()
        result = self.classifier(text, self.candidate_labels)
        return result['labels'], result['scores']

        

class BatchProcessor:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.task = None # Do not start automatically

    def start(self):
        if self.task is None:
            self.loop = asyncio.get_event_loop()
            self.task = self.loop.create_task(self._batch_processor_task())
            print(">>> BatchProcessor task started.")

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                print(">>> BatchProcessor task stopped.")
            self.task = None

    async def add_request(self, prompt: str) -> str:
        if self.task is None:
            raise RuntimeError("BatchProcessor is not running. Call start() first.")
        future = self.loop.create_future()
        await self.queue.put((prompt, future))
        return await future

    async def _batch_processor_task(self):
        while True:
            try:
                # 1. Wait for the first request
                first_prompt, first_future = await self.queue.get()
                
                prompts = [first_prompt]
                futures = [first_future]
                
                # 2. Collect more requests until BATCH_SIZE or BATCH_TIMEOUT
                while len(prompts) < BATCH_SIZE:
                    try:
                        # Wait for a short time for more items
                        prompt, future = await asyncio.wait_for(self.queue.get(), timeout=BATCH_TIMEOUT)
                        prompts.append(prompt)
                        futures.append(future)
                    except asyncio.TimeoutError:
                        # Timeout reached, process the current batch
                        break
                
                # 3. Process the batch
                if prompts:
                    print(f">>> Processing batch of size: {len(prompts)}")
                    try:
                        summaries = await _call_ollama_batch(prompts)
                        # 4. Distribute results
                        for i, future in enumerate(futures):
                            if not future.done():
                                future.set_result(summaries[i])
                    except Exception as e:
                        # If batch processing fails, notify all futures
                        for future in futures:
                            if not future.done():
                                future.set_exception(e)

            except Exception as e:
                print(f"Error in batch processor task: {e}")
                # Avoid task crashing on unexpected errors
                await asyncio.sleep(1)

# --- Service Instantiation ---
batch_processor = BatchProcessor()
sentiment_analyzer = SentimentAnalyzer()
conversation_tagger = ConversationTagger()

# --- End of Hugging Face Model ---

def _format_conversation(conversation: Conversation) -> str:
    """Formats a list of conversation turns into a single string."""
    convo_text = []
    for turn in conversation:
        for speaker, text in turn.items():
            convo_text.append(f"{speaker}: {text}")
    return "\n".join(convo_text)

async def _call_ollama(prompt: str) -> str:
    """Helper function to call the Ollama API and get the response."""
    api_url = f"{settings.OLLAMA_API_URL}/api/generate"
    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False
    }
    
    async with llm_semaphore:
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

async def summarize_text(request: Conversation) -> SummaryResponse:
    """Generates a summary for the given conversation using the batch processor."""
    full_text = _format_conversation(request)
    prompt = f"다음 상담 내용을 세 문장으로 요약해줘.\n\n---\n{full_text}\n---"
    
    # Use the batch processor instead of a direct call
    summary = await batch_processor.add_request(prompt)
    
    return SummaryResponse(summary=summary)

async def tag_keywords(request: Conversation) -> TaggingResponse:
    """classify conversations by pre-set labels"""
    full_text = _format_conversation(request)
    tags, tag_scores = conversation_tagger.tagging(full_text)
    print(tags, tag_scores)
    tags = tags[0:2]
    
    return TaggingResponse(tags=tags)

async def analyze_emotion(request: Conversation) -> EmotionResponse:
    """Analyzes the emotion of the given conversation using the Hugging Face model."""
    full_text = _format_conversation(request)
    emotion = sentiment_analyzer.analyze(full_text)
    return EmotionResponse(emotion=emotion)