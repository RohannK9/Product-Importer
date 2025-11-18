"""Pydantic schemas for webhook resources."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WebhookBase(BaseModel):
    name: str
    target_url: HttpUrl
    event: str = Field(..., description="Event name e.g. product.imported")
    headers: Dict[str, str] | None = None
    is_enabled: bool = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    target_url: Optional[HttpUrl] = None
    event: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    is_enabled: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    items: list[WebhookResponse]


class WebhookTestResponse(BaseModel):
    status: str
    response_code: int | None = None
    response_time_ms: int | None = None
    response_body: str | None = None


class WebhookDeliveryResponse(BaseModel):
    id: UUID
    event: str
    status: str
    response_code: int | None
    response_time_ms: int | None
    created_at: datetime

    class Config:
        from_attributes = True
