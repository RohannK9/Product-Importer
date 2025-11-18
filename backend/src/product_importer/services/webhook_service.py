"""Webhook management and dispatch helpers."""

from __future__ import annotations

import httpx
from typing import Iterable
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from product_importer.core.config import get_settings
from product_importer.models.webhook import Webhook, WebhookDelivery
from product_importer.schemas.webhook import (
    WebhookCreate,
    WebhookDeliveryResponse,
    WebhookResponse,
    WebhookUpdate,
)

settings = get_settings()


class WebhookService:
    def __init__(self, db: Session):
        self.db = db

    def list_webhooks(self) -> list[Webhook]:
        stmt = select(Webhook).order_by(Webhook.created_at.desc())
        return self.db.scalars(stmt).all()

    def get(self, webhook_id: UUID) -> Webhook:
        webhook = self.db.get(Webhook, webhook_id)
        if not webhook:
            raise ValueError("Webhook not found")
        return webhook

    def create(self, payload: WebhookCreate) -> Webhook:
        webhook = Webhook(**payload.model_dump())
        self.db.add(webhook)
        self.db.flush()
        return webhook

    def update(self, webhook_id: UUID, payload: WebhookUpdate) -> Webhook:
        webhook = self.get(webhook_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(webhook, key, value)
        self.db.add(webhook)
        self.db.flush()
        return webhook

    def delete(self, webhook_id: UUID) -> None:
        webhook = self.get(webhook_id)
        self.db.delete(webhook)

    def list_deliveries(self, webhook_id: UUID, limit: int = 25) -> list[WebhookDelivery]:
        stmt = (
            select(WebhookDelivery)
            .where(WebhookDelivery.webhook_id == webhook_id)
            .order_by(desc(WebhookDelivery.created_at))
            .limit(limit)
        )
        return self.db.scalars(stmt).all()

    def list_active_for_event(self, event: str) -> list[Webhook]:
        stmt = select(Webhook).where(Webhook.event == event, Webhook.is_enabled.is_(True))
        return self.db.scalars(stmt).all()

    def record_delivery(
        self,
        webhook: Webhook,
        *,
        event: str,
        payload: dict,
        response_code: int | None,
        response_time_ms: int | None,
        response_body: str | None,
        status: str,
    ) -> WebhookDelivery:
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event=event,
            payload=payload,
            response_code=response_code,
            response_time_ms=response_time_ms,
            response_body=response_body,
            status=status,
        )
        self.db.add(delivery)
        self.db.flush()
        return delivery

    async def test_webhook(self, webhook_id: UUID) -> dict:
        webhook = self.get(webhook_id)
        async with httpx.AsyncClient(timeout=settings.webhook_request_timeout) as client:
            response = await client.post(webhook.target_url, json={"event": webhook.event, "test": True})
        return {
            "status": "ok" if response.is_success else "failed",
            "response_code": response.status_code,
            "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            "response_body": response.text,
        }

    @staticmethod
    def serialize(webhook: Webhook) -> WebhookResponse:
        return WebhookResponse.model_validate(webhook)

    @staticmethod
    def serialize_many(webhooks: Iterable[Webhook]) -> list[WebhookResponse]:
        return [WebhookResponse.model_validate(hook) for hook in webhooks]

    @staticmethod
    def serialize_deliveries(deliveries: Iterable[WebhookDelivery]) -> list[WebhookDeliveryResponse]:
        return [WebhookDeliveryResponse.model_validate(delivery) for delivery in deliveries]
