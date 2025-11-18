"""Filesystem-based storage helpers."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile


class FileStorage:
    """Persist uploaded files to disk safely."""

    def __init__(self, base_dir: str, *, max_size_bytes: int | None = None) -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_bytes

    def save_upload(self, upload_file: UploadFile) -> Tuple[str, str, int]:
        original_name = upload_file.filename or "upload.csv"
        extension = Path(original_name).suffix or ".csv"
        unique_name = f"{uuid.uuid4()}{extension}"
        destination = self.base_path / unique_name

        total_bytes = 0
        upload_file.file.seek(0)
        with destination.open("wb") as buffer:
            while True:
                chunk = upload_file.file.read(1024 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if self.max_size_bytes and total_bytes > self.max_size_bytes:
                    buffer.close()
                    destination.unlink(missing_ok=True)
                    raise ValueError("Uploaded file exceeds allowed size")
                buffer.write(chunk)
        upload_file.file.seek(0)

        return original_name, str(destination), total_bytes

    def delete(self, stored_path: str) -> None:
        try:
            os.remove(stored_path)
        except FileNotFoundError:
            return
