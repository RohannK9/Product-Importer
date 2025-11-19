"""S3-based cloud storage implementation."""

from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path
from typing import Tuple

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from loguru import logger


class S3Storage:
    """Store and retrieve files from AWS S3 (or S3-compatible services)."""

    def __init__(
        self,
        bucket_name: str,
        *,
        endpoint_url: str | None = None,
        region_name: str = "us-east-1",
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        max_size_bytes: int | None = None,
    ) -> None:
        """Initialize S3 client.

        Args:
            bucket_name: S3 bucket name
            endpoint_url: Custom S3 endpoint (for Cloudflare R2, MinIO, etc.)
            region_name: AWS region
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            max_size_bytes: Maximum file size allowed
        """
        self.bucket_name = bucket_name
        self.max_size_bytes = max_size_bytes

        # Initialize S3 client
        session = boto3.session.Session()
        self.s3_client = session.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

        # Verify bucket exists
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Connected to S3 bucket: {bucket_name}")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "404":
                logger.error(f"S3 bucket '{bucket_name}' does not exist")
            elif error_code == "403":
                logger.error(f"Access denied to S3 bucket '{bucket_name}'")
            else:
                logger.error(f"Error connecting to S3 bucket: {e}")
            raise

    def save_upload(self, upload_file: UploadFile) -> Tuple[str, str, int]:
        """Save uploaded file to S3.

        Args:
            upload_file: FastAPI UploadFile object

        Returns:
            Tuple of (original_filename, s3_path, file_size_bytes)
        """
        original_name = upload_file.filename or "upload.csv"
        extension = Path(original_name).suffix or ".csv"
        unique_name = f"uploads/{uuid.uuid4()}{extension}"

        # Read file content
        upload_file.file.seek(0)
        file_content = upload_file.file.read()
        total_bytes = len(file_content)

        # Check file size
        if self.max_size_bytes and total_bytes > self.max_size_bytes:
            raise ValueError(f"File size ({total_bytes} bytes) exceeds maximum allowed size")

        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_name,
                Body=file_content,
                ContentType=upload_file.content_type or "text/csv",
                Metadata={
                    "original_filename": original_name,
                },
            )
            logger.info(f"Uploaded file to S3: {unique_name} ({total_bytes} bytes)")
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise

        # Reset file pointer for potential re-reading
        upload_file.file.seek(0)

        # Return S3 path (s3://bucket/key format)
        s3_path = f"s3://{self.bucket_name}/{unique_name}"
        return original_name, s3_path, total_bytes

    def download_to_path(self, s3_path: str, local_path: Path) -> None:
        """Download file from S3 to local path.

        Args:
            s3_path: S3 URI (s3://bucket/key)
            local_path: Local destination path
        """
        # Parse S3 path
        if not s3_path.startswith("s3://"):
            raise ValueError(f"Invalid S3 path: {s3_path}")

        parts = s3_path[5:].split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid S3 path format: {s3_path}")

        bucket_name, key = parts

        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Download from S3
        try:
            self.s3_client.download_file(bucket_name, key, str(local_path))
            logger.info(f"Downloaded S3 file {key} to {local_path}")
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {e}")
            raise

    def get_file_content(self, s3_path: str) -> bytes:
        """Get file content directly from S3 as bytes.

        Args:
            s3_path: S3 URI (s3://bucket/key)

        Returns:
            File content as bytes
        """
        # Parse S3 path
        if not s3_path.startswith("s3://"):
            raise ValueError(f"Invalid S3 path: {s3_path}")

        parts = s3_path[5:].split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid S3 path format: {s3_path}")

        bucket_name, key = parts

        # Download from S3 to memory
        try:
            buffer = BytesIO()
            self.s3_client.download_fileobj(bucket_name, key, buffer)
            buffer.seek(0)
            return buffer.read()
        except ClientError as e:
            logger.error(f"Failed to get file content from S3: {e}")
            raise

    def delete(self, s3_path: str) -> None:
        """Delete file from S3.

        Args:
            s3_path: S3 URI (s3://bucket/key)
        """
        # Parse S3 path
        if not s3_path.startswith("s3://"):
            logger.warning(f"Invalid S3 path for deletion: {s3_path}")
            return

        parts = s3_path[5:].split("/", 1)
        if len(parts) != 2:
            logger.warning(f"Invalid S3 path format for deletion: {s3_path}")
            return

        bucket_name, key = parts

        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=key)
            logger.info(f"Deleted S3 file: {key}")
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            # Don't raise - deletion failures shouldn't break the app
