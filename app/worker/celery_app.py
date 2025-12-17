from celery import Celery

from app.config import settings

celery_app = Celery(
    "ytdlp_worker",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,  # Process one task at a time
    result_expires=86400,  # Results expire after 24 hours
)
