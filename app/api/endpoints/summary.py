from fastapi import APIRouter, Body
from typing import List
from celery.result import AsyncResult

from core.celery_config import celery_app
from app.tasks import summarize_task
from app.schemas import ConversationTurn

router = APIRouter()

@router.post("/summary", tags=["Summary"], status_code=202)
async def post_summary(request: List[ConversationTurn] = Body(...)):
    """
    Accepts a conversation and starts a background task to summarize it.
    Returns a task ID for polling the result.
    """
    conversation_dicts = [turn.dict() for turn in request]
    task = summarize_task.delay(conversation_dicts)
    return {"task_id": task.id}

@router.get("/results/{task_id}", tags=["Summary"])
async def get_summary_result(task_id: str):
    """
    Retrieves the result of a summary task.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.ready():
        if task_result.successful():
            return {"status": "SUCCESS", "summary": task_result.get()}
        else:
            return {"status": "FAILURE", "error": str(task_result.info)}
    else:
        return {"status": task_result.status}