"""Dependency injection for storage backend."""

from __future__ import annotations

from product_importer.core.config import get_settings
from product_importer.services.s3_storage import S3Storage
from product_importer.services.storage import FileStorage

settings = get_settings()


def get_storage() -> FileStorage | S3Storage:
    """Get the configured storage backend."""
    if settings.storage_backend == "s3":
        if not settings.s3_bucket_name:
            raise ValueError("S3_BUCKET_NAME must be set when using S3 storage backend")
        
        return S3Storage(
            bucket_name=settings.s3_bucket_name,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            max_size_bytes=settings.max_upload_size_mb * 1024 * 1024,
        )
    else:
        return FileStorage(
            base_dir=settings.upload_tmp_dir,
            max_size_bytes=settings.max_upload_size_mb * 1024 * 1024,
        )
