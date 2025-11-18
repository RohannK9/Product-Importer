"""Webhook dispatch tasks."""

from __future__ import annotations

import time
from typing import Any

import httpx
from celery import shared_task
from loguru import logger

from product_importer.core.config import get_settings
from product_importer.db.session import SessionLocal
from product_importer.services.webhook_service import WebhookService

settings = get_settings()


def _dispatch_single_webhook(service: WebhookService, hook, event: str, payload: dict[str, Any]) -> None:
    headers = hook.headers or {}
    started = time.perf_counter()
    status = "success"
    response_code = None
    response_body: str | None = None

    try:
        with httpx.Client(timeout=settings.webhook_request_timeout) as client:
            response = client.post(
                hook.target_url,
                json={"event": event, "payload": payload},
                headers=headers,
            )
        response_code = response.status_code
        response_body = response.text[:2000]
        if not response.is_success:
            status = "failed"
    except Exception as exc:  # noqa: BLE001
        logger.exception("Webhook %s failed", hook.id)
        status = "failed"
        response_body = str(exc)
    finally:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        service.record_delivery(
            hook,
            event=event,
            payload=payload,
            response_code=response_code,
            response_time_ms=elapsed_ms,
            response_body=response_body,
            status=status,
        )


@shared_task(bind=True, max_retries=3, name="dispatch_webhook_event")
def dispatch_webhook_event(self, event: str, payload: dict[str, Any]) -> None:
    session = SessionLocal()
    try:
        service = WebhookService(session)
        hooks = service.list_active_for_event(event)
        if not hooks:
            logger.info("No webhooks registered for %s", event)
            return

        for hook in hooks:
            _dispatch_single_webhook(service, hook, event, payload)
            session.commit()

    except Exception as exc:  # noqa: BLE001
        session.rollback()
        logger.exception("Failed dispatching event %s", event)
        raise self.retry(exc=exc, countdown=10)
    finally:
        session.close()
