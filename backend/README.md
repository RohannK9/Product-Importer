# Product Importer Backend

Backend service for handling CSV ingestion, product CRUD, and webhook automation.

## Local development

```bash
cd backend
poetry install
poetry run uvicorn product_importer.main:app --reload
```

Environment variables are loaded from `../.env`. Copy `.env.example` to `.env` and update secrets as needed.

## Docker / Compose

At repo root:

```bash
docker compose up --build
```

Services started:

1. `postgres`: primary database (default port 5432)
2. `redis`: broker/result backend for Celery (port 6379)
3. `api`: FastAPI application served via Uvicorn (port 8000)
4. `worker`: Celery worker handling CSV ingestion & webhook dispatch

Mounts share `backend/src` and `storage` for live reloads and uploaded files.

## Testing

```bash
poetry run pytest
```

Additional quality tools: `poetry run ruff check` and `poetry run black .`.
