"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Liveness probe")
def liveness() -> dict[str, str]:
    return {"status": "ok"}
