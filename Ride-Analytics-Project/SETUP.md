# Setup Guide

This guide will help you set up and run the Ride-Sharing Analytics Pipeline on GCP.

## 📦 Single Bucket Architecture

**Important**: This project uses a **single GCS bucket** (`ride-analytics`) with organized folders:

```
ride-analytics/
├── bronze/              # Raw data (Bronze layer)
│   ├── drivers/
│   │   └── drivers.csv
│   ├── passengers/
│   │   └── passengers.csv
│   └── rides/
│       └── YYYY-MM-DD/
│           └── rides.csv
├── silver/              # Processed data (Silver layer)
│   ├── rides_processed/
│   ├── drivers_processed/
│   └── passengers_processed/
├── spark-jobs/          # Spark scripts and artifacts
│   └── *.py
└── quality-reports/     # Data quality reports
    └── YYYY-MM-DD/
```

All data layers and Spark jobs are organized within this single bucket using folders.

## Prerequisites

1. **GCP Account** with billing enabled
2. **Python 3.9+** installed
3. **Google Cloud SDK** installed and configured
4. **Git** installed

## Step 1: Clone and Setup Project

```bash
cd "Project Class 3"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r scripts/requirements.txt
```

## Step 2: Configure GCP Project

Set up authentication:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**Note**: Ensure all GCP resources (GCS bucket, Dataproc cluster, Composer, BigQuery) are already created.

## Step 3: Generate Sample Data

```bash
python scripts/generate_sample_data.py
```

This will create sample data in `data/raw/` directory:
- `drivers.csv` - Driver master data
- `passengers.csv` - Passenger master data
- `rides/YYYY-MM-DD/rides.csv` - Daily ride data

## Step 4: Create/Verify GCS Bucket Structure

**Important**: You need a **single GCS bucket** named `ride-analytics` (or your preferred name) with the following folder structure:

```bash
# Create bucket (if not exists)
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://ride-analytics || echo "Bucket already exists"

# Create folder structure (folders are created automatically when files are uploaded)
# No need to create empty folders, they will be created when you upload files
```

**Folder structure inside the bucket**:
- `bronze/` - Raw data landing zone
- `silver/` - Processed/cleaned data
- `spark-jobs/` - Spark Python scripts
- `quality-reports/` - Data quality check reports

**Other GCP Resources Required**:
- **BigQuery dataset**: `ridesharing_analytics` (will be created if not exists)
- **Managed Dataproc cluster** (must be already running)
- **Cloud Composer environment** (if not already created)

## Step 5: Upload Sample Data to GCS

**Note**: The data generation script creates files in `data/raw/` directory (relative to where you run the script).

```bash
# Set your bucket name (default: ride-analytics)
BUCKET_NAME="ride-analytics"

# Upload drivers and passengers (creates folders automatically)
gsutil cp data/raw/drivers.csv gs://$BUCKET_NAME/bronze/drivers/
gsutil cp data/raw/passengers.csv gs://$BUCKET_NAME/bronze/passengers/

# Upload rides data (preserves date folder structure)
gsutil -m cp -r data/raw/rides/* gs://$BUCKET_NAME/bronze/rides/
```

**Verify upload**:
```bash
gsutil ls -r gs://$BUCKET_NAME/bronze/
```

**Note**: For automated deployment, use the CI/CD pipeline (see Step 7).

## Step 6: Manual Deployment (Alternative to CI/CD)

If you prefer to deploy manually instead of using CI/CD:

```bash
# Set your bucket name
BUCKET_NAME="ride-analytics"

# Upload Spark jobs
gsutil -m cp spark/jobs/*.py gs://$BUCKET_NAME/spark-jobs/

# Upload BigQuery connector JAR (if needed)
gsutil cp gs://spark-lib/bigquery/spark-bigquery-latest.jar gs://$BUCKET_NAME/spark-jobs/ || true
```

## Step 7: Ensure Dataproc Cluster is Running

**Note**: You should have a managed Dataproc cluster already running in GCP.

Verify your cluster is running:
```bash
gcloud dataproc clusters list --region=us-central1
```

Update the environment variables in the Airflow DAG or set them in Composer:
- `DATAPROC_CLUSTER_NAME` (default: `ridesharing-cluster`)
- `GCS_BUCKET_NAME` (default: `ride-analytics`)
- `BIGQUERY_DATASET` (default: `ridesharing_analytics`)

## Step 8: Setup CI/CD Pipeline (Recommended)

Configure GitHub Secrets:
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `GCP_SA_KEY`: Service account JSON key with required permissions
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCS_BUCKET_NAME`: Your GCS bucket name (default: `ride-analytics`)
   - `DATAPROC_CLUSTER_NAME`: Your Dataproc cluster name (default: `ridesharing-cluster`)
   - `COMPOSER_ENVIRONMENT`: Composer environment name (default: `ridesharing-composer`)
   - `COMPOSER_REGION`: Composer region (default: `us-central1`)

3. Push to main branch or manually trigger the workflow
4. The workflow will automatically deploy:
   - Spark jobs to `gs://{bucket}/spark-jobs/`
   - Airflow DAGs to Composer
   - Verify all resources

## Step 9: Create Cloud Composer Environment (if not already created)

```bash
gcloud composer environments create ridesharing-composer \
    --location us-central1 \
    --node-count 3 \
    --machine-type n1-standard-1 \
    --disk-size 30GB
```

Wait for the environment to be created (takes ~20-30 minutes).

**Note**: Skip this step if Cloud Composer is already created.

## Step 10: Upload Airflow DAGs (if not using CI/CD)

```bash
# Get Composer bucket name
COMPOSER_BUCKET=$(gcloud composer environments describe ridesharing-composer \
    --location us-central1 \
    --format="get(config.dagGcsPrefix)")

# Upload DAGs
gsutil cp airflow/dags/*.py $COMPOSER_BUCKET/dags/
```

**Note**: If using CI/CD, DAGs are automatically deployed on push to main.

## Step 11: Configure Airflow DAG Environment Variables

Set environment variables in Composer:
1. Go to Cloud Composer → Environments → Your Environment
2. Click "Edit" → "Environment variables"
3. Add:
   - `GCP_PROJECT_ID`: Your project ID
   - `GCS_BUCKET_NAME`: `ride-analytics` (or your bucket name)
   - `DATAPROC_CLUSTER_NAME`: Your cluster name
   - `BIGQUERY_DATASET`: `ridesharing_analytics`

## Step 12: Run the Pipeline

1. Go to Cloud Composer UI
2. Find the `rides_pipeline_dag` DAG
3. Trigger it manually or wait for scheduled execution

## Step 11: Verify Pipeline Execution

Check the pipeline execution in Cloud Composer UI:
1. Go to Cloud Composer → Environments → ridesharing-composer
2. Click on "Airflow" to open Airflow UI
3. Find `rides_pipeline_dag` and check execution status
4. View task logs for any issues

## Troubleshooting

### Pipeline fails at data quality check
- Check the quality report in GCS: `gs://ride-analytics/quality-reports/`
- Review data quality issues and fix source data

### BigQuery load fails
- Check BigQuery permissions
- Verify Spark BigQuery connector JAR is available
- Check GCS bucket permissions
- Verify Dataproc cluster has BigQuery access

### Dataproc job fails
- Check Dataproc cluster is running: `gcloud dataproc clusters list`
- Verify cluster name matches the DAG configuration (set via environment variable)
- Check cluster logs in Cloud Console
- Ensure Spark jobs are uploaded to GCS: `gsutil ls gs://ride-analytics/spark-jobs/`

### CI/CD deployment fails
- Verify GitHub Secrets are configured correctly
- Check GCP service account has required permissions:
  - Storage Object Admin (for GCS)
  - Dataproc Editor (for Dataproc)
  - Composer Worker (for Composer)
- Verify bucket exists: `gsutil ls gs://ride-analytics`

## Code Formatting

**Important**: This project uses [Black](https://black.readthedocs.io/) for code formatting. All Python code must be formatted according to Black's standards before committing.

### Formatting Your Code

Before committing code, ensure it's properly formatted:

```bash
# Install Black
pip install black

# Format all Spark job files
black spark/jobs/*.py

# Check formatting without making changes (used in CI)
black --check spark/jobs
```

**Note**: The CI pipeline will fail if code is not properly formatted. Always format your code before pushing to GitHub.

## Running Spark Tests Locally

### Quick Start

**Prerequisites:**
- Python 3.9+ installed
- Java 11 or 17 installed (required for PySpark)
  - Check: `java -version`
  - Install if needed: `brew install openjdk@11` (macOS) or download from [Adoptium](https://adoptium.net/)

**Quick Test Run:**

```bash
# 1. Navigate to project
cd "Project Class 3/Ride-Analytics-Project"

# 2. Activate virtual environment (if you have one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install test tools
pip install pytest pytest-cov

# 4. Install dependencies for Spark tests
pip install -r spark/requirements.txt

# 5. Run Spark tests
cd spark
pytest tests/ -v
cd ..
```

That's it! If all tests pass, you're good to go. See detailed instructions below for more options.

### Detailed: Running Spark/PySpark Tests

**Basic test run:**
```bash
# Step 1: Go to spark directory
cd spark

# Step 2: Run all tests
pytest tests/ -v

# Step 3: Go back to project root
cd ..
```

**Other useful commands:**

Run tests with coverage report (shows which lines of code were tested):
```bash
cd spark
pytest tests/ -v --cov=jobs --cov-report=html
# Then open htmlcov/index.html in your browser to see the report
cd ..
```

Run only one test file:
```bash
cd spark
pytest tests/test_transformations.py -v
cd ..
```

Run only one specific test function:
```bash
cd spark
pytest tests/test_transformations.py::test_haversine_distance -v
cd ..
```

**Note**: Spark tests require Java to be installed. If you get a "Java not found" error, install Java first (see Troubleshooting section below).


### Troubleshooting Common Issues

**Problem: `Java not found` error when running Spark tests**

**Solution:** Install Java first, then set the JAVA_HOME variable.

On macOS:
```bash
brew install openjdk@11
export JAVA_HOME=$(/usr/libexec/java_home -v 11)
```

On Linux:
```bash
sudo apt-get install openjdk-11-jdk
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

On Windows:
- Download Java 11 from [Adoptium](https://adoptium.net/)
- Install it
- Set JAVA_HOME environment variable in System Settings

**Problem: `ModuleNotFoundError`**

**Solution:** Make sure you're in the correct directory when running tests.
- You must be in the `spark` directory when running Spark tests: `cd spark`
- The test file tries to import from `../jobs`, so make sure you're in the `spark` folder

**Problem: `SparkContext already initialized`**

**Solution:** This happens when Spark session wasn't closed properly. Just restart your terminal and try again.

**Problem: `PYTHON_VERSION_MISMATCH` - Python in worker has different version than driver**

**Error message:**
```
PySparkRuntimeError: [PYTHON_VERSION_MISMATCH] Python in worker has different version (3, 9) than that in driver 3.11
```

**Solution:** Set the PYSPARK_PYTHON and PYSPARK_DRIVER_PYTHON environment variables to use the same Python version:

```bash
# Before running tests, set these environment variables
export PYSPARK_PYTHON=$(which python3.11)  # or python3, python3.9, etc.
export PYSPARK_DRIVER_PYTHON=$(which python3.11)

# Then run tests
cd spark
pytest tests/ -v
```

Or add this to your test file (already included in `test_transformations.py`):
```python
import sys
import os
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
```

**Note:** Make sure you're using the same Python version that you installed PySpark with. Check your Python version:
```bash
python3 --version  # or python3.11 --version
```

### Test Coverage

**Local Testing:**

To generate an HTML coverage report (shows which lines of code were tested):

```bash
cd spark
pytest tests/ --cov=jobs --cov-report=html
cd ..
# Then open spark/htmlcov/index.html in your browser to see the report
```

**CI/CD (GitHub Actions):**

When Spark tests run in GitHub Actions, HTML coverage reports are automatically generated and uploaded as artifacts. To view them:

1. **After a workflow run completes:**
   - Go to your GitHub repository
   - Click on the **"Actions"** tab
   - Click on the workflow run you want to view
   - Scroll down to the **"Artifacts"** section at the bottom
   - You'll see:
     - `spark-coverage-report` - HTML coverage for Spark tests

2. **Download the artifact:**
   - Click on the artifact name (e.g., `spark-coverage-report`)
   - Click the **"Download"** button
   - Extract the downloaded ZIP file
   - Open `htmlcov/index.html` in your browser to view the coverage report

3. **View coverage summary:**
   - In the workflow run page, check the **"Summary"** section
   - You'll see a coverage summary with links and instructions

**Coverage Reports:**
- **HTML Report**: Interactive report showing line-by-line coverage (available as artifact)
- **XML Report**: Machine-readable format (uploaded to Codecov if configured)
- **Terminal Output**: Coverage summary in the workflow logs

**Note:** 
- Artifacts are retained for 30 days by default

## Running FastAPI

The FastAPI application provides REST API endpoints to query analytics data from BigQuery. 

**Two deployment options:**
- **Local Development**: Run locally for testing (see below)
- **Cloud Run Deployment**: Deployed automatically via GitHub Actions (globally accessible)

### Which Method Should I Use?

**Recommended for most users:**
- ✅ **`run_api.sh` script** - Simplest and easiest way to run the API locally
  - Automatically checks dependencies
  - Sets up environment
  - Prompts for missing configuration
  - Best for quick local development

**Alternative methods:**
- **Direct uvicorn command** - If you prefer manual control
- **Docker** - If you want containerized local development (optional)

### Prerequisites

1. **Python 3.9+** installed
2. **GCP Authentication** configured:
   - Application Default Credentials (ADC) set up
   - Or service account key file
3. **BigQuery Dataset** with processed data (Gold layer must be populated)

### Step 1: Set Up Virtual Environment

```bash
# Navigate to project root
cd "Project Class 3/Ride-Analytics-Project"

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### Step 2: Install API Dependencies

```bash
# Install API requirements
pip install -r api/requirements.txt
```

### Step 3: Configure GCP Authentication

**Option A: Application Default Credentials (Recommended)**

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set your GCP project
gcloud config set project YOUR_PROJECT_ID
```

**Option B: Service Account Key**

```bash
# Set environment variable to point to your service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

# On Windows:
# set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json
```

**Required Permissions:**
- BigQuery Data Viewer
- BigQuery Job User

### Step 4: Set Environment Variables

```bash
# Set GCP project ID
export GCP_PROJECT_ID="your-gcp-project-id"

# Set BigQuery dataset name (default: ridesharing_analytics)
export BIGQUERY_DATASET="ridesharing_analytics"

# On Windows:
# set GCP_PROJECT_ID=your-gcp-project-id
# set BIGQUERY_DATASET=ridesharing_analytics
```

**Or create a `.env` file** in the project root (optional):

```bash
# .env file
GCP_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=ridesharing_analytics
```

Then install `python-dotenv` and load it:
```bash
pip install python-dotenv
```

### Step 5: Verify BigQuery Data

Before running the API, ensure your BigQuery dataset has data:

```bash
# Check if dataset exists
bq ls ridesharing_analytics

# Check if tables exist
bq ls ridesharing_analytics | grep -E "agg_daily_rides|agg_driver_performance|dim_drivers"

# Query to verify data
bq query --use_legacy_sql=false "SELECT COUNT(*) as count FROM \`your-project.ridesharing_analytics.agg_daily_rides\`"
```

### Step 6: Run the API Server

**🎯 Option A: Using the Quick Start Script (RECOMMENDED)**

This is the easiest way - the script handles everything automatically:

```bash
# Navigate to project root
cd "Project Class 3/Ride-Analytics-Project"

# Make script executable (first time only)
chmod +x run_api.sh

# Run the script
./run_api.sh
```

The script will:
- ✅ Check and create virtual environment if needed
- ✅ Install dependencies automatically
- ✅ Prompt for GCP project ID if not set
- ✅ Check GCP authentication
- ✅ Start the API server

**Option B: Using uvicorn directly**

If you prefer manual control:

```bash
# Navigate to project root
cd "Project Class 3/Ride-Analytics-Project"

# Activate virtual environment
source venv/bin/activate

# Set environment variables (if not already set)
export GCP_PROJECT_ID="your-gcp-project-id"
export BIGQUERY_DATASET="ridesharing_analytics"

# Run the API
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
```

**Option C: Using Docker (Optional - for containerized local development)**

If you want to run the API in a Docker container:

```bash
# Navigate to api directory
cd api

# Build the Docker image
docker build -t ride-analytics-api .

# Run the container
docker run -d \
  -p 8080:8080 \
  -e GCP_PROJECT_ID="your-gcp-project-id" \
  -e BIGQUERY_DATASET="ridesharing_analytics" \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  --name ride-api \
  ride-analytics-api
```

**Note:** For Docker, you need to mount your GCP credentials or use a service account key file.

**Which should I use?**
- 🎯 **Use `run_api.sh`** - If you just want to get started quickly (recommended)
- **Use uvicorn directly** - If you want more control over the process
- **Use Docker** - If you prefer containerized development or want to isolate dependencies

### Step 7: Access the API

Once the server is running, you'll see:

```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Available endpoints:**

1. **Root endpoint** (API information):
   ```
   http://localhost:8080/
   ```

2. **Interactive API documentation (Swagger UI)**:
   ```
   http://localhost:8080/docs
   ```

3. **Alternative API documentation (ReDoc)**:
   ```
   http://localhost:8080/redoc
   ```

4. **Health check**:
   ```
   http://localhost:8080/api/health
   ```

5. **Daily rides**:
   ```
   http://localhost:8080/api/rides/daily?date=2025-01-15
   # Or without date (uses today)
   http://localhost:8080/api/rides/daily
   ```

6. **Driver performance**:
   ```
   http://localhost:8080/api/drivers/DRV000001
   ```

7. **Revenue summary**:
   ```
   http://localhost:8080/api/revenue/summary?start_date=2025-01-01&end_date=2025-01-31
   ```

### Step 8: Test the API

**Using curl:**

```bash
# Health check
curl http://localhost:8080/api/health

# Daily rides (today)
curl http://localhost:8080/api/rides/daily

# Daily rides (specific date)
curl "http://localhost:8080/api/rides/daily?date=2025-01-15"

# Driver performance
curl http://localhost:8080/api/drivers/DRV000001

# Revenue summary
curl "http://localhost:8080/api/revenue/summary?start_date=2025-01-01&end_date=2025-01-31"
```

**Using the Interactive Docs (Swagger UI):**

1. Open `http://localhost:8080/docs` in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Enter parameters if needed
5. Click "Execute"
6. View the response

**Using Python requests:**

```python
import requests

# Health check
response = requests.get("http://localhost:8080/api/health")
print(response.json())

# Daily rides
response = requests.get("http://localhost:8080/api/rides/daily?date=2025-01-15")
print(response.json())

# Driver performance
response = requests.get("http://localhost:8080/api/drivers/DRV000001")
print(response.json())

# Revenue summary
response = requests.get(
    "http://localhost:8080/api/revenue/summary",
    params={"start_date": "2025-01-01", "end_date": "2025-01-31"}
)
print(response.json())
```

### Troubleshooting

**1. Authentication Errors**

```
Error: Could not automatically determine credentials
```

**Solution:**
```bash
# Set up Application Default Credentials
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

**2. BigQuery Permission Errors**

```
Error: Access Denied: BigQuery BigQuery: Permission denied
```

**Solution:**
- Ensure your account/service account has:
  - `BigQuery Data Viewer` role
  - `BigQuery Job User` role
- Grant permissions:
  ```bash
  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@example.com" \
    --role="roles/bigquery.dataViewer"
  
  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="user:your-email@example.com" \
    --role="roles/bigquery.jobUser"
  ```

**3. Table Not Found Errors**

```
Error: Not found: Table your-project:ridesharing_analytics.agg_daily_rides
```

**Solution:**
- Ensure the pipeline has run and populated BigQuery tables
- Check dataset name matches `BIGQUERY_DATASET` environment variable
- Verify tables exist:
  ```bash
  bq ls ridesharing_analytics
  ```

**4. Port Already in Use**

```
Error: [Errno 48] Address already in use
```

**Solution:**
- Use a different port:
  ```bash
  uvicorn api.main:app --port 8081 --reload
  ```
- Or kill the process using the port:
  ```bash
  # Find process
  lsof -ti:8080
  # Kill it
  kill -9 $(lsof -ti:8080)
  ```

**5. Module Not Found**

```
Error: No module named 'fastapi'
```

**Solution:**
- Ensure virtual environment is activated
- Reinstall requirements:
  ```bash
  pip install -r api/requirements.txt
  ```

### Environment Variables Summary

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GCP_PROJECT_ID` | Your GCP project ID | `your-gcp-project-id` | Yes |
| `BIGQUERY_DATASET` | BigQuery dataset name | `ridesharing_analytics` | No |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key | - | Optional* |

*Required if not using Application Default Credentials

### Quick Start - Summary

**For Quick Setup (Recommended):**
```bash
cd "Project Class 3/Ride-Analytics-Project"
./run_api.sh
```
That's it! The script handles everything.

**For Manual Setup:**
```bash
source venv/bin/activate
export GCP_PROJECT_ID="your-project-id"
uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
```

**The `run_api.sh` script is already included in the project** - you don't need to create it. Just run it!

### API Endpoints Summary

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | API information | None |
| `/api/health` | GET | Health check | None |
| `/api/rides/daily` | GET | Daily ride metrics | `date` (optional, YYYY-MM-DD) |
| `/api/drivers/{driver_id}` | GET | Driver performance | `driver_id` (path) |
| `/api/revenue/summary` | GET | Revenue summary | `start_date`, `end_date` (required) |

### Next Steps - Local Development

Once the API is running locally:
1. Test all endpoints using Swagger UI (`/docs`)
2. Verify endpoints work correctly
3. Test with real BigQuery data
4. When ready, deploy to Cloud Run (see below)

## Deploying FastAPI to Cloud Run

The FastAPI is automatically deployed to Cloud Run when you push to the `main` branch via GitHub Actions.

### How It Works

1. **Automatic Deployment**: When you push to `main` branch, the CD pipeline:
   - Builds the Docker image using Cloud Build
   - Pushes to Artifact Registry
   - Deploys to Cloud Run (creates service if it doesn't exist)
   - Makes it globally accessible
   - Grants necessary BigQuery permissions

2. **Required GitHub Secrets**:
   - `GCP_SA_KEY`: Service account JSON key (required)
   - `GCP_PROJECT_ID`: GCP project ID (required)
   
   **Optional** (with defaults):
   - `CLOUD_RUN_SERVICE_NAME`: Service name (defaults to 'ride-analytics-api')
   - `CLOUD_RUN_REGION`: Region (defaults to 'us-central1')
   - `BIGQUERY_DATASET`: Dataset name (defaults to 'ridesharing_analytics')

3. **Service Account Permissions**:
   The GitHub Actions service account (`GCP_SA_KEY`) needs:
   - Cloud Build Service Account
   - Cloud Run Admin
   - Artifact Registry Writer
   - IAM Security Admin
   - Storage Object Admin
   - BigQuery Data Editor

### After Deployment

Once deployed, you'll get a **global API URL** like:
```
https://ride-analytics-api-xxxxx-uc.a.run.app
```

**Access the API:**
- **API Root**: `https://your-service-url/`
- **API Docs**: `https://your-service-url/docs` (Swagger UI)
- **Health Check**: `https://your-service-url/api/health`
- **Endpoints**: Same as local, but using the Cloud Run URL

### Manual Deployment (if needed)

If you want to deploy manually:

```bash
# Build and deploy using gcloud
cd api

# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ride-analytics-api

# Deploy to Cloud Run
gcloud run deploy ride-analytics-api \
  --image gcr.io/YOUR_PROJECT_ID/ride-analytics-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=YOUR_PROJECT_ID,BIGQUERY_DATASET=ridesharing_analytics"
```

### Viewing Deployment Status

After pushing to `main` branch:
1. Go to GitHub → Actions tab
2. Click on the latest workflow run
3. View the deployment summary at the bottom
4. Copy the Cloud Run service URL

### Testing Deployed API

```bash
# Replace with your actual service URL
SERVICE_URL="https://ride-analytics-api-xxxxx-uc.a.run.app"

# Health check
curl $SERVICE_URL/api/health

# Daily rides
curl "$SERVICE_URL/api/rides/daily?date=2025-01-15"

# Driver performance
curl "$SERVICE_URL/api/drivers/DRV000001"

# Revenue summary
curl "$SERVICE_URL/api/revenue/summary?start_date=2025-01-01&end_date=2025-01-31"
```

### Troubleshooting: "Error: Forbidden" on Cloud Run

If you see "Error: Forbidden" when accessing your Cloud Run service, it means public access is not enabled. Fix it by running:

```bash
# Replace with your actual service name and region
gcloud run services add-iam-policy-binding ride-analytics-api \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

**Or via GCP Console:**
1. Go to Cloud Run in GCP Console
2. Click on your service name
3. Go to "Permissions" tab
4. Click "Grant Access"
5. Add principal: `allUsers`
6. Select role: `Cloud Run Invoker`
7. Save

**Note:** The GitHub Actions workflow now automatically grants public access during deployment, so future deployments should work without this manual step.

## Next Steps

Once the pipeline is running:
1. Push code to `main` branch to trigger Cloud Run deployment
2. Access the deployed API using the Cloud Run URL
3. Set up monitoring and alerting using Cloud Monitoring
4. Configure additional CI/CD pipeline settings (see `.github/workflows/README.md`)
5. Add more data quality checks

