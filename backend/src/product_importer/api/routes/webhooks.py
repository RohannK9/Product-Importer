"""Webhook configuration endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from product_importer.db.deps import get_db
from product_importer.schemas.webhook import (
    WebhookCreate,
    WebhookDeliveryResponse,
    WebhookListResponse,
    WebhookResponse,
    WebhookTestResponse,
    WebhookUpdate,
)
from product_importer.services.webhook_service import WebhookService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> WebhookService:
    return WebhookService(db)


@router.get("/", response_model=WebhookListResponse)
def list_webhooks(service: WebhookService = Depends(get_service)) -> WebhookListResponse:
    hooks = service.list_webhooks()
    return WebhookListResponse(items=WebhookService.serialize_many(hooks))


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    payload: WebhookCreate,
    service: WebhookService = Depends(get_service),
) -> WebhookResponse:
    try:
        hook = service.create(payload)
        return WebhookService.serialize(hook)
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Duplicate webhook") from exc


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(webhook_id: UUID, service: WebhookService = Depends(get_service)) -> WebhookResponse:
    try:
        hook = service.get(webhook_id)
        return WebhookService.serialize(hook)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{webhook_id}", response_model=WebhookResponse)
@router.patch("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: UUID,
    payload: WebhookUpdate,
    service: WebhookService = Depends(get_service),
) -> WebhookResponse:
    try:
        hook = service.update(webhook_id, payload)
        return WebhookService.serialize(hook)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    response_class=Response,
)
def delete_webhook(webhook_id: UUID, service: WebhookService = Depends(get_service)) -> Response:
    try:
        service.delete(webhook_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(webhook_id: UUID, service: WebhookService = Depends(get_service)) -> WebhookTestResponse:
    try:
        result = await service.test_webhook(webhook_id)
        return WebhookTestResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{webhook_id}/deliveries", response_model=list[WebhookDeliveryResponse])
def webhook_deliveries(webhook_id: UUID, service: WebhookService = Depends(get_service)) -> list[WebhookDeliveryResponse]:
    try:
        deliveries = service.list_deliveries(webhook_id)
        return WebhookService.serialize_deliveries(deliveries)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
