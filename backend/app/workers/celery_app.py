import os
from celery import Celery
from app.core.config import settings

# Initialize Celery
celery_app = Celery(
    "bravola_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Industry Standard Configuration for Reliability
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # Force kill tasks stuck for > 10 mins
    worker_concurrency=4, # Adjust based on your CPU cores
)