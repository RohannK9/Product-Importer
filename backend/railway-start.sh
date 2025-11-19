#!/bin/bash

# Railway startup script for Product Importer
set -e

echo "Starting Product Importer..."

# Wait for database to be ready
echo "Waiting for database connection..."
python3 -c "
import time
from sqlalchemy import create_engine, text
from product_importer.core.config import get_settings

settings = get_settings()
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('Database is ready!')
        break
    except Exception as e:
        retry_count += 1
        print(f'Database not ready yet... ({retry_count}/{max_retries})')
        time.sleep(2)
        if retry_count >= max_retries:
            raise Exception('Database connection timeout')
"

echo "Database connection established"

# Start the application
echo "Starting uvicorn server..."
exec uvicorn product_importer.main:app --host 0.0.0.0 --port ${PORT:-8000}
