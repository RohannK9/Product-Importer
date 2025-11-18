"""CSV ingestion workflow task."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator

from celery import shared_task
from loguru import logger
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from product_importer.core.config import get_settings
from product_importer.db.session import SessionLocal
from product_importer.models.product import Product
from product_importer.models.upload_job import UploadJob, UploadStatus

settings = get_settings()


def chunked_reader(file_path: Path, chunk_size: int = 2000) -> Iterator[list[dict[str, str]]]:
    with file_path.open("r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        batch: list[dict[str, str]] = []
        for row in reader:
            batch.append(row)
            if len(batch) >= chunk_size:
                yield batch
                batch = []
        if batch:
            yield batch


@shared_task(bind=True, max_retries=3, name="product_ingestion")
def ingest_products_from_csv(self, job_id: str) -> None:
    session: Session = SessionLocal()
    try:
        job = session.get(UploadJob, job_id)
        if not job:
            logger.error("Upload job %s not found", job_id)
            return

        file_path = Path(job.storage_path)
        job.status = UploadStatus.PARSING
        session.add(job)
        session.commit()

        total_processed = 0
        for batch in chunked_reader(file_path):
            job.status = UploadStatus.UPSERTING
            session.add(job)
            session.commit()

            upsert_map: dict[str, dict[str, object]] = {}
            for raw_row in batch:
                normalized: dict[str, object] = {}
                for key, value in (raw_row or {}).items():
                    cleaned_key = (key or "").strip().lower()
                    if not cleaned_key:
                        continue
                    base_key = cleaned_key.split("_", 1)[0]
                    if isinstance(value, str):
                        cleaned_value: object = value.strip()
                    else:
                        cleaned_value = value
                    # prefer exact key match over derived base key
                    if cleaned_key == base_key or base_key not in normalized:
                        normalized[base_key] = cleaned_value
                    elif base_key in normalized:
                        # keep first seen base value
                        continue

                sku = (normalized.get("sku") or "").strip() if isinstance(normalized.get("sku"), str) else normalized.get("sku", "")
                if not sku:
                    continue
                try:
                    price_value = normalized.get("price", "0") or "0"
                    price = Decimal(price_value) if not isinstance(price_value, Decimal) else price_value
                except InvalidOperation:
                    price = Decimal("0")

                name_value = normalized.get("name", "")
                if isinstance(name_value, str):
                    name_value = name_value or sku
                else:
                    name_value = sku

                description_value = normalized.get("description")
                if isinstance(description_value, str):
                    description_value = description_value.strip()

                currency_value = normalized.get("currency", "USD") or "USD"
                if isinstance(currency_value, str):
                    currency_value = currency_value.upper()
                else:
                    currency_value = "USD"

                is_active_value = normalized.get("is_active", "true")
                if isinstance(is_active_value, str):
                    is_active = is_active_value.lower() != "false"
                else:
                    is_active = bool(is_active_value)

                upsert_map[str(sku)] = {
                    "sku": str(sku),
                    "name": name_value,
                    "description": description_value,
                    "price": price,
                    "currency": currency_value,
                    "is_active": is_active,
                }

            upserts = list(upsert_map.values())
            if not upserts:
                continue

            stmt = pg_insert(Product.__table__).values(upserts)
            stmt = stmt.on_conflict_do_update(
                index_elements=[Product.sku],
                set_={
                    "name": stmt.excluded.name,
                    "description": stmt.excluded.description,
                    "price": stmt.excluded.price,
                    "currency": stmt.excluded.currency,
                    "is_active": stmt.excluded.is_active,
                },
            )
            session.execute(stmt)
            total_processed += len(upserts)
            job.processed_rows = total_processed
            session.add(job)
            session.commit()

        job.status = UploadStatus.COMPLETED
        job.total_rows = total_processed
        session.add(job)
        session.commit()
        logger.info("Job %s completed with %s rows", job_id, total_processed)

    except Exception as exc:
        session.rollback()
        logger.exception("Failed job %s", job_id)
        job = session.get(UploadJob, job_id)
        if job:
            job.status = UploadStatus.FAILED
            error_message = str(exc)
            if len(error_message) > 900:
                error_message = error_message[:900] + "…"
            job.error = error_message
            session.add(job)
            session.commit()
        raise self.retry(exc=exc, countdown=10)
    finally:
        session.close()
