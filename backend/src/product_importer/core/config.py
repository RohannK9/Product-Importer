"""Application configuration via Pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="Product Importer API")
    environment: str = Field(default="development")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    log_level: str = Field(default="info")

    allowed_origins: str | None = Field(default=None)

    @property
    def allowed_origins_list(self) -> List[str]:
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    database_url: str
    postgres_schema: str = Field(default="product_app")

    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    upload_tmp_dir: str = Field(default="/tmp/uploads")
    max_upload_size_mb: int = Field(default=600)
    webhook_request_timeout: float = Field(default=5.0)
    webhook_max_retries: int = Field(default=3)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
