"""Database session utilities."""

from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from product_importer.core.config import get_settings

settings = get_settings()

db_engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
metadata = MetaData(schema=settings.postgres_schema)
Base = declarative_base(metadata=metadata)


@contextmanager
def db_session():
    """Provide a transactional scope around a series of operations."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
