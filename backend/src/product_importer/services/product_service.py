"""Business logic for product operations."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from product_importer.models.product import Product
from product_importer.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from product_importer.services.events import emit_event


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def list_products(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        sku: Optional[str] = None,
        query: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Product], int]:
        stmt = select(Product)
        count_stmt = select(func.count()).select_from(Product)

        filters = []
        if sku:
            filters.append(func.lower(Product.sku) == sku.lower())
        if query:
            like = f"%{query}%"
            filters.append(or_(Product.name.ilike(like), Product.description.ilike(like)))
        if is_active is not None:
            filters.append(Product.is_active.is_(is_active))

        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        stmt = stmt.order_by(Product.created_at.desc())
        total = self.db.scalar(count_stmt) or 0
        items = self.db.execute(
            stmt.offset((page - 1) * page_size).limit(page_size)
        ).scalars().all()
        return items, total

    def get(self, product_id: int) -> Product:
        product = self.db.get(Product, product_id)
        if not product:
            raise NoResultFound
        return product

    def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        self.db.flush()
        emit_event("product.created", self._serialize(product))
        return product

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get(product_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        self.db.add(product)
        self.db.flush()
        emit_event("product.updated", self._serialize(product))
        return product

    def delete(self, product_id: int) -> None:
        product = self.get(product_id)
        payload = self._serialize(product)
        self.db.delete(product)
        emit_event("product.deleted", payload)

    def bulk_delete(self) -> int:
        deleted = self.db.query(Product).delete()
        count = deleted or 0
        if count:
            emit_event("product.bulk_deleted", {"count": count})
        return count

    @staticmethod
    def _serialize(product: Product) -> dict:
        return ProductResponse.model_validate(product).model_dump()
