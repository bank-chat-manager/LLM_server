from celery import Celery
from kombu import Queue

# Redis를 브로커 및 백엔드로 사용하는 Celery 앱 인스턴스 생성
celery_app = Celery(
    'bank_chat_manager',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['app.tasks']
)

# --- 큐 정의 ---
# default_queue: 일반적인 짧은 작업을 위한 기본 큐
# long_task_queue: 처리 시간이 긴 작업을 위한 전용 큐
celery_app.conf.task_queues = (
    Queue('default_queue', routing_key='task.default'),
    Queue('long_task_queue', routing_key='task.long'),
)

# --- 라우팅 규칙 정의 ---
# 작업 이름에 'report'가 포함된 경우 'long_task_queue'로 보냄
# 그 외 모든 작업은 'default_queue'로 보냄
celery_app.conf.task_routes = {
    'app.tasks.generate_report_task': {
        'queue': 'long_task_queue',
        'routing_key': 'task.long',
    },
    # 다른 모든 작업은 기본 큐로 라우팅됩니다.
    # 'app.tasks.summarize_task': {
    #     'queue': 'default_queue',
    #     'routing_key': 'task.default',
    # },
}

# Celery 앱 설정 업데이트
celery_app.conf.update(
    task_track_started=True,
)