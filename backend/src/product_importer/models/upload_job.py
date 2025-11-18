"""Upload job status tracking."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from product_importer.models.base import Base, TimestampMixin, UUIDPrimaryKey


class UploadStatus(str, enum.Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    PARSING = "parsing"
    VALIDATING = "validating"
    UPSERTING = "upserting"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadJob(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "upload_jobs"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    total_rows: Mapped[int | None] = mapped_column(Integer)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[UploadStatus] = mapped_column(
        Enum(UploadStatus, native_enum=False, length=32), nullable=False
    )
    error: Mapped[str | None] = mapped_column(String(1024))
