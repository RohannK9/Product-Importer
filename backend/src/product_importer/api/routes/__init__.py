"""API route registration."""

from fastapi import APIRouter

from product_importer.api.routes import health, products, uploads, webhooks

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

__all__ = ["router"]
