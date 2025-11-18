"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from product_importer.api.routes import router as api_router
from product_importer.core.config import get_settings
from product_importer.db.session import Base, db_engine

settings = get_settings()

app = FastAPI(title=settings.app_name)


def _init_database() -> None:
    schema_name = settings.postgres_schema
    with db_engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    Base.metadata.create_all(bind=db_engine)


_init_database()

allowed_origins = settings.allowed_origins_list
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


@app.get("/", tags=["health"], summary="Root probe")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}
