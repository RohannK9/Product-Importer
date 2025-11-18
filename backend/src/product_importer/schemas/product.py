"""Pydantic models for products."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    sku: str = Field(..., description="Stock keeping unit, unique and case-insensitive")
    name: str
    description: Optional[str] = None
    price: float = 0
    currency: str = "USD"
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int


class BulkDeleteRequest(BaseModel):
    confirmation_text: str = Field(
        ..., description="User-entered confirmation text that must match DELETE ALL"
    )


class BulkDeleteResponse(BaseModel):
    deleted_count: int
