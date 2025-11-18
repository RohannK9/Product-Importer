To Run this applciation, Clone it using: git clone https://github.com/RohannK9/Product-Importer.git
Navigate to frontend folder by: cd web
Then Install the dependencies of Vite and React by: npm install
Create a .env file and add: VITE_API_BASE_URL=http://localhost:8000
Run the frontend using: npm run dev

To run the backend for this project, navigate to the backend folder using command: cd backend
Then create a .env file and add the following components: POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=<YOUR DB NAME>
POSTGRES_USER=<YOUR DB USERNAME>
POSTGRES_PASSWORD=<YOUR DB PASSWORD>
POSTGRES_SCHEMA=<YOUR DB SCHEMA_NAME>
DATABASE_URL=postgresql+psycopg://<YOUR DB USERNAME>:<YOUR DB PASSWORD>@localhost:5432/<YOUR DB NAME>

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

UPLOAD_TMP_DIR=./storage/uploads
MAX_UPLOAD_SIZE_MB=600

FRONTEND_URL=http://localhost:5173

After adding the above variables inside .env, run the command: docker compose up --build
