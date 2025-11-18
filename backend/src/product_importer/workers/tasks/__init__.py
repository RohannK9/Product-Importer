"""Celery task namespace with explicit imports for autodiscovery."""

from .ingestion import ingest_products_from_csv
from .webhooks import dispatch_webhook_event

__all__ = [
    "ingest_products_from_csv",
    "dispatch_webhook_event",
]
