FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN mkdir -p /app/storage

ENV MODULE_NAME=product_importer.main \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

EXPOSE 8000

CMD ["uvicorn", "product_importer.main:app", "--host", "0.0.0.0", "--port", "8000"]
