"""Upload job orchestration services."""

from __future__ import annotations

from typing import Iterable
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from product_importer.models.upload_job import UploadJob, UploadStatus
from product_importer.schemas.upload import UploadJobResponse
from product_importer.services.storage import FileStorage


class UploadService:
    def __init__(self, db: Session, storage: FileStorage | None = None):
        self.db = db
        self.storage = storage

    def enqueue(self, upload_file: UploadFile) -> UploadJob:
        if not self.storage:
            raise ValueError("Storage backend is required for enqueueing uploads")

        original_name, stored_path, _ = self.storage.save_upload(upload_file)

        job = UploadJob(
            filename=original_name,
            storage_path=stored_path,
            status=UploadStatus.RECEIVED,
            processed_rows=0,
        )
        self.db.add(job)
        self.db.flush()

        # Kick off Celery ingestion task lazily to avoid circular import at module load time.
        from product_importer.workers.tasks.ingestion import ingest_products_from_csv

        job.status = UploadStatus.QUEUED
        self.db.add(job)
        self.db.flush()
        self.db.commit()

        ingest_products_from_csv.delay(str(job.id))

        return job

    def get_job(self, job_id: UUID | str) -> UploadJob:
        job_uuid = UUID(str(job_id))
        job = self.db.get(UploadJob, job_uuid)
        if not job:
            raise ValueError("Upload job not found")
        return job

    def list_jobs(self, limit: int = 50) -> list[UploadJob]:
        stmt = select(UploadJob).order_by(UploadJob.created_at.desc()).limit(limit)
        return self.db.scalars(stmt).all()

    @staticmethod
    def serialize(job: UploadJob) -> UploadJobResponse:
        return UploadJobResponse.model_validate(job)

    @staticmethod
    def serialize_many(jobs: Iterable[UploadJob]) -> list[UploadJobResponse]:
        return [UploadJobResponse.model_validate(job) for job in jobs]
