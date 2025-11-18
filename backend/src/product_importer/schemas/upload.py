"""Schemas related to upload jobs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from product_importer.models.upload_job import UploadStatus


class UploadJobResponse(BaseModel):
    id: UUID
    filename: str
    total_rows: int | None
    processed_rows: int
    status: UploadStatus
    error: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UploadJobListResponse(BaseModel):
    items: list[UploadJobResponse]


class UploadInitResponse(BaseModel):
    job_id: UUID
    status: UploadStatus
