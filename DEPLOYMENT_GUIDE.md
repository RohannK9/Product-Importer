# Complete Deployment Guide - Product Importer

## Prerequisites

- ✅ Code pushed to GitHub (Done!)
- Railway account
- Vercel account
- GitHub repository: `RohannK9/Product-Importer`

---

## Part 1: Railway Backend Deployment

### Step 1: Create New Project on Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose repository: `RohannK9/Product-Importer`
5. Railway will create the project

### Step 2: Add Postgres Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will provision a Postgres database
5. Note: Railway will automatically set the `DATABASE_URL` variable

### Step 3: Add Redis

1. Click **"+ New"** again
2. Select **"Database"**
3. Choose **"Add Redis"**
4. Railway will provision Redis
5. Note: Railway will automatically set the `REDIS_URL` variable

### Step 4: Configure Backend API Service

1. Click on your main service (created from GitHub)
2. Go to **"Settings"** tab
3. Under **"Root Directory"**, set: `backend`
4. Under **"Start Command"**, set:
   ```bash
   uvicorn product_importer.main:app --host 0.0.0.0 --port $PORT
   ```

5. Go to **"Variables"** tab
6. Click **"+ New Variable"** and add these one by one:

   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   POSTGRES_SCHEMA = product_app
   REDIS_URL = ${{Redis.REDIS_URL}}
   CELERY_BROKER_URL = ${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND = ${{Redis.REDIS_URL}}
   ALLOWED_ORIGINS = *
   APP_NAME = Product Importer API
   ENVIRONMENT = production
   ```

   > **Note**: We'll update `ALLOWED_ORIGINS` with the Vercel URL later

7. Click **"Deploy"** to trigger deployment

### Step 5: Create Celery Worker Service

1. Click **"+ New"** in your Railway project
2. Select **"GitHub Repo"**
3. Choose the same repository: `RohannK9/Product-Importer`
4. Rename this service to **"worker"** (click the service name at top)
5. Go to **"Settings"** tab
6. Under **"Root Directory"**, set: `backend`
7. Under **"Start Command"**, set:
   ```bash
   celery -A product_importer.workers.celery_app.celery_app worker --loglevel=info
   ```

8. Go to **"Variables"** tab
9. Add the **SAME variables** as the API service:

   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   POSTGRES_SCHEMA = product_app
   REDIS_URL = ${{Redis.REDIS_URL}}
   CELERY_BROKER_URL = ${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND = ${{Redis.REDIS_URL}}
   ```

10. Click **"Deploy"**

### Step 6: Verify Railway Backend Deployment

#### Check API Service

1. Click on your **API service**
2. Go to **"Deployments"** tab - wait for deployment to complete (green checkmark)
3. Go to **"Settings"** → **"Networking"** → Click **"Generate Domain"**
4. **Copy the generated URL** (e.g., `https://your-app.up.railway.app`)
5. Open this URL in your browser - you should see:
   ```json
   {"service": "Product Importer API", "status": "ok"}
   ```

6. Go to **"Logs"** tab and verify you see:
   ```
   INFO: Starting database initialization...
   INFO: Connected to database: PostgreSQL
   INFO: Created schema: product_app
   INFO: Created tables in schema 'product_app': ['products', 'upload_jobs', 'webhooks']
   INFO: Database initialization completed successfully
   ```

#### Check Worker Service

1. Click on your **Worker service**
2. Go to **"Deployments"** tab - wait for deployment to complete
3. Go to **"Logs"** tab and verify you see:
   ```
   [INFO/MainProcess] Connected to redis://...
   [INFO/MainProcess] celery@<hostname> ready.
   ```
   
   ✅ **No errors** about "Module 'product_importer' has no attribute 'celery'"

#### Check Database Tables

1. Click on your **Postgres service**
2. Go to **"Data"** tab
3. In the schema dropdown, select: `product_app`
4. You should see three tables:
   - `products`
   - `upload_jobs`
   - `webhooks`

---

## Part 2: Vercel Frontend Deployment

### Step 1: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Click **"Import"** next to `RohannK9/Product-Importer`
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `web`
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `.next` (should auto-detect)

### Step 2: Configure Environment Variables

1. Before deploying, scroll to **"Environment Variables"**
2. Add this variable:
   
   **Key**: `NEXT_PUBLIC_API_URL`  
   **Value**: `https://your-railway-api-url.up.railway.app` (paste from Railway step 6.4)
   
   > Make sure there's **NO trailing slash** at the end!

3. Click **"Deploy"**
4. Wait for deployment to complete (usually 1-2 minutes)

### Step 3: Get Vercel URL

1. Once deployed, Vercel will show your app URL (e.g., `https://product-importer-xyz.vercel.app`)
2. **Copy this URL**

### Step 4: Update Railway CORS Configuration

1. Go back to **Railway**
2. Click on your **API service**
3. Go to **"Variables"** tab
4. Find the `ALLOWED_ORIGINS` variable
5. Update it to your Vercel URL:
   ```
   https://product-importer-xyz.vercel.app
   ```
   
   > Multiple origins: `https://app1.vercel.app,https://app2.vercel.app`

6. The API service will automatically redeploy

---

## Part 3: Final Verification

### ✅ Test Backend API

1. Open: `https://your-railway-api-url.up.railway.app`
2. Should return: `{"service": "Product Importer API", "status": "ok"}`

### ✅ Test Frontend

1. Open your Vercel app URL
2. The app should load without errors

### ✅ Test CSV Upload (End-to-End)

1. Open your Vercel app
2. Create a test CSV file:
   ```csv
   name,description,price,stock
   Test Product,A test product,29.99,100
   Another Product,Another test,49.99,50
   ```
3. Click **"Upload CSV"** (or similar button)
4. Select your CSV file
5. Click **"Start Upload"**

**Expected Results:**
- ✅ Upload shows "Queued" status
- ✅ Status changes to "Processing"
- ✅ Status changes to "Completed"
- ✅ No "Network Error" messages
- ✅ Browser console has no CORS errors

### ✅ Verify in Railway Database

1. Go to Railway → Postgres service → **"Data"** tab
2. Schema: `product_app`
3. Table: `products`
4. You should see your uploaded products!

---

## Troubleshooting

### Issue: API Returns 500 Error

**Check:**
- Railway API logs for errors
- Database initialization completed successfully
- All environment variables are set

**Fix:**
- Redeploy the API service
- Check that `DATABASE_URL` references Postgres correctly

### Issue: Worker Shows Module Import Error

**Error**: `Module 'product_importer' has no attribute 'celery'`

**Fix:**
- Verify the worker start command is:
  ```bash
  celery -A product_importer.workers.celery_app.celery_app worker --loglevel=info
  ```
- Note the **double** `celery_app` in the command

### Issue: Frontend Shows "Network Error"

**Check:**
1. Browser console for CORS errors
2. `NEXT_PUBLIC_API_URL` in Vercel settings
3. `ALLOWED_ORIGINS` in Railway API service

**Fix:**
- Update `ALLOWED_ORIGINS` to include your Vercel URL
- Ensure no trailing slashes in URLs
- Redeploy both services

### Issue: Upload Gets Stuck on "Processing"

**Check:**
- Railway Worker logs for errors
- Redis connection in worker logs
- Worker shows "ready" status

**Fix:**
- Restart the Worker service
- Verify `REDIS_URL` and `CELERY_BROKER_URL` are set correctly

---

## Summary of Services

| Service | Platform | URL Variable | Purpose |
|---------|----------|--------------|---------|
| Postgres | Railway | `DATABASE_URL` | Database storage |
| Redis | Railway | `REDIS_URL` | Celery message broker |
| API | Railway | `NEXT_PUBLIC_API_URL` | FastAPI backend |
| Worker | Railway | - | Celery task processor |
| Frontend | Vercel | - | Next.js web app |

---

## Environment Variables Quick Reference

### Railway API Service
```bash
DATABASE_URL = ${{Postgres.DATABASE_URL}}
POSTGRES_SCHEMA = product_app
REDIS_URL = ${{Redis.REDIS_URL}}
CELERY_BROKER_URL = ${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND = ${{Redis.REDIS_URL}}
ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
APP_NAME = Product Importer API
ENVIRONMENT = production
```

### Railway Worker Service
```bash
DATABASE_URL = ${{Postgres.DATABASE_URL}}
POSTGRES_SCHEMA = product_app
REDIS_URL = ${{Redis.REDIS_URL}}
CELERY_BROKER_URL = ${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND = ${{Redis.REDIS_URL}}
```

### Vercel Frontend
```bash
NEXT_PUBLIC_API_URL = https://your-railway-api-url.up.railway.app
```

---

## Done! 🎉

Your Product Importer is now fully deployed and operational!

- Backend API: Railway
- Celery Worker: Railway
- Database: Railway Postgres
- Cache/Broker: Railway Redis
- Frontend: Vercel
