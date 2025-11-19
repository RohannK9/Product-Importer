"""FastAPI application entrypoint."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from product_importer.api.routes import router as api_router
from product_importer.core.config import get_settings
from product_importer.db.session import Base, db_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title=settings.app_name)


def _init_database() -> None:
    """Initialize database schema and tables."""
    try:
        logger.info("Starting database initialization...")
        logger.info(f"Database URL: {settings.database_url.split('@')[-1]}")  # Log without credentials
        
        schema_name = settings.postgres_schema
        logger.info(f"Creating schema: {schema_name}")
        
        # Test connection first
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Connected to database: {version}")
        
        # Create extension and schema
        with db_engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
            logger.info("Created citext extension")
            
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            logger.info(f"Created schema: {schema_name}")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=db_engine)
        
        # Verify tables were created
        with db_engine.connect() as conn:
            result = conn.execute(
                text(
                    f"SELECT table_name FROM information_schema.tables "
                    f"WHERE table_schema = '{schema_name}'"
                )
            )
            tables = [row[0] for row in result]
            logger.info(f"Created tables in schema '{schema_name}': {tables}")
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise


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
