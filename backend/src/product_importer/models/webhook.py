"""Webhook configuration models."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from product_importer.models.base import Base, TimestampMixin, UUIDPrimaryKey


class Webhook(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "webhooks"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_url: Mapped[str] = mapped_column(String(512), nullable=False)
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    headers: Mapped[dict | None] = mapped_column(JSON, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class WebhookDelivery(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "webhook_delivery_logs"

    webhook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_app.webhooks.id", ondelete="CASCADE"), nullable=False
    )
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    response_code: Mapped[int | None] = mapped_column(Integer)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    response_body: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
