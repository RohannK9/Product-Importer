"""FastAPI dependencies for database access."""

from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from product_importer.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
