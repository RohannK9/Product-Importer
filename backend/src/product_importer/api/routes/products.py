"""Product API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from product_importer.db.deps import get_db
from product_importer.schemas.product import (
    BulkDeleteRequest,
    BulkDeleteResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from product_importer.services.product_service import ProductService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.get("/", response_model=ProductListResponse, summary="List products")
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sku: str | None = None,
    query: str | None = None,
    is_active: bool | None = None,
    service: ProductService = Depends(get_service),
) -> ProductListResponse:
    items, total = service.list_products(
        page=page,
        page_size=page_size,
        sku=sku,
        query=query,
        is_active=is_active,
    )
    return ProductListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_service),
) -> ProductResponse:
    try:
        product = service.create(payload)
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail="SKU must be unique") from exc
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def retrieve_product(
    product_id: int,
    service: ProductService = Depends(get_service),
) -> ProductResponse:
    try:
        return service.get(product_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc


@router.put("/{product_id}", response_model=ProductResponse)
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: ProductService = Depends(get_service),
) -> ProductResponse:
    try:
        return service.update(product_id, payload)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_service),
) -> None:
    try:
        service.delete(product_id)
    except NoResultFound as exc:
        raise HTTPException(status_code=404, detail="Product not found") from exc


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
def bulk_delete(
    payload: BulkDeleteRequest,
    service: ProductService = Depends(get_service),
) -> BulkDeleteResponse:
    if payload.confirmation_text.strip().upper() != "DELETE ALL":
        raise HTTPException(status_code=400, detail="Confirmation text mismatch")
    deleted = service.bulk_delete()
    return BulkDeleteResponse(deleted_count=deleted)
