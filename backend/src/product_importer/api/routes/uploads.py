"""Upload endpoints for CSV ingestion."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from product_importer.core.config import get_settings
from product_importer.db.deps import get_db
from product_importer.schemas.upload import UploadInitResponse, UploadJobListResponse, UploadJobResponse
from product_importer.services.storage import FileStorage
from product_importer.services.upload_service import UploadService

router = APIRouter()
settings = get_settings()


def get_storage() -> FileStorage:
    return FileStorage(settings.upload_tmp_dir, max_size_bytes=settings.max_upload_size_mb * 1024 * 1024)


def get_service(db=Depends(get_db), storage: FileStorage = Depends(get_storage)) -> UploadService:
    return UploadService(db, storage)


@router.post("/", response_model=UploadInitResponse, summary="Start upload")
async def upload_file(
    file: UploadFile = File(...),
    service: UploadService = Depends(get_service),
) -> UploadInitResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    job = service.enqueue(file)
    return UploadInitResponse(job_id=job.id, status=job.status)


@router.get("/{job_id}", response_model=UploadJobResponse, summary="Get job status")
def job_status(job_id: str, service: UploadService = Depends(get_service)) -> UploadJobResponse:
    try:
        job = service.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return UploadService.serialize(job)


@router.get("/", response_model=UploadJobListResponse, summary="Recent jobs")
def recent_jobs(service: UploadService = Depends(get_service)) -> UploadJobListResponse:
    jobs = service.list_jobs()
    return UploadJobListResponse(items=UploadService.serialize_many(jobs))
