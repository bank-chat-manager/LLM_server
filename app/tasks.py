import httpx
import json
import time
from typing import List

from core.celery_config import celery_app
from core.config import settings
from .schemas import ConversationTurn


def _format_conversation(conversation: List[ConversationTurn]) -> str:
    """Formats a list of conversation turns into a single string."""
    return "\n".join([f"{turn.speaker}: {turn.text}" for turn in conversation])


async def _call_ollama_async(prompt: str) -> str:
    """Helper function to call the Ollama API and get the response."""
    api_url = f"{settings.OLLAMA_API_URL}/api/generate"
    payload = {
        "model": "qwen2:0.5b",  # Using the optimized model
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
        
        except Exception as e:
            # In a real-world scenario, you might want to retry the task
            return f"LLM API 호출 중 알 수 없는 오류 발생: {e}"


@celery_app.task(name="app.tasks.summarize_task")
def summarize_task(conversation: List[dict]) -> str:
    """Celery task to generate a summary for the given conversation."""
    import asyncio

    formatted_text = "\n".join([f"{turn['speaker']}: {turn['text']}" for turn in conversation])
    
    prompt = f"다음 상담 내용을 세 문장으로 요약해줘.\n\n---\n{formatted_text}\n---"
    
    summary = asyncio.run(_call_ollama_async(prompt))
    return summary

@celery_app.task(name="app.tasks.generate_report_task")
def generate_report_task(user_id: str) -> dict:
    """
    A long-running task to simulate report generation.
    This task will take at least 30 seconds.
    """
    print(f"Starting report generation for user: {user_id}...")
    time.sleep(30)  # Simulate long processing time
    result = {
        "user_id": user_id,
        "report_url": f"/reports/{user_id}_summary_report.pdf"
    }
    print(f"Finished report generation for user: {user_id}.")
    return result
