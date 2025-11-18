"""Celery application instance."""

from __future__ import annotations

from celery import Celery

from product_importer.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "product_importer",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
)

celery_app.conf.update(
    task_track_started=True,
    worker_send_task_events=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["product_importer.workers.tasks"])

__all__ = ["celery_app"]
