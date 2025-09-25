from fastapi import APIRouter, Body

from app.tasks import generate_report_task

router = APIRouter()

@router.post("/reports", tags=["Reports"], status_code=202)
async def post_create_report(request: dict = Body(...)):
    """
    Accepts a request to generate a long-running report.
    The task is sent to the 'long_task_queue'.
    """
    user_id = request.get("user_id", "default_user")
    
    # .apply_async를 사용하여 명시적으로 큐를 지정합니다.
    # celery_config.py의 라우팅 규칙에 의해 자동으로 지정되지만, 명시하는 것이 더 안전합니다.
    task = generate_report_task.apply_async(args=[user_id], queue='long_task_queue')
    
    return {"task_id": task.id, "message": "Report generation started."}
