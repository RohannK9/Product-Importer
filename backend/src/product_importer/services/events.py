"""Simple helper to emit domain events via Celery tasks."""

from __future__ import annotations

from loguru import logger

try:
    from product_importer.workers.tasks.webhooks import dispatch_webhook_event
except ModuleNotFoundError:  # pragma: no cover
    dispatch_webhook_event = None


def emit_event(event: str, payload: dict) -> None:
    """Send an asynchronous webhook dispatch task if the worker is available."""

    if dispatch_webhook_event is None:
        logger.warning("Webhook dispatch task not available; skipping event %s", event)
        return

    logger.debug("Emitting event %s", event)
    dispatch_webhook_event.delay(event, payload)
