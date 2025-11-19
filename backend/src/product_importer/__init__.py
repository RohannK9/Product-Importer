"""Product Importer backend package."""

from product_importer.workers.celery_app import celery_app

__all__ = ["celery_app"]
