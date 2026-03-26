# GitHub Actions Workflows Guide

This project uses two GitHub Actions workflows for CI/CD automation.

---

## 📋 Overview

### 1. **CI Pipeline** (`ci.yml`) - Continuous Integration
   - **Purpose**: Test and validate code quality
   - **When it runs**: On every push and pull request
   - **What it does**: Lints code, runs tests, validates Airflow DAGs

### 2. **CD Pipeline** (`deploy.yml`) - Continuous Deployment
   - **Purpose**: Deploy code to GCP
   - **When it runs**: On push to `main` branch or manual trigger
   - **What it does**: 
     - Uploads Spark jobs and Airflow DAGs to GCP
     - **Deploys FastAPI to Cloud Run** (globally accessible API)

---

## 🔍 Detailed Workflow Explanation

### **CI Pipeline** (`ci.yml`)

#### **Triggers:**
```yaml
on:
  push:
    branches: [ main, dev ]    # Runs when code is pushed to main/dev
  pull_request:
    branches: [ main, dev ]    # Runs when a PR is opened/updated
```

**Runs on:**
- Every push to `main` or `dev` branches
- Every pull request targeting `main` or `dev`

#### **Jobs:**

##### **Job 1: `lint`** - Code Quality Checks
- **Purpose**: Check code style and formatting
- **Steps**:
  1. Checkout code from repository
  2. Set up Python 3.9
  3. Install linting tools (flake8, black)
  4. Run flake8 to check for errors
  5. Run black to check code formatting
- **Fails if**: Code has syntax errors or doesn't follow formatting standards

##### **Job 2: `test-spark`** - Run Spark Tests
- **Purpose**: Test Spark/PySpark code
- **Steps**:
  1. Checkout code
  2. Set up Python 3.9
  3. Install Java 11 (required for PySpark)
  4. Install PySpark and test dependencies
  5. Set up environment variables (PYSPARK_PYTHON, PYTHONPATH)
  6. Run pytest with coverage
  7. Upload coverage reports (XML to Codecov, HTML as artifact)
  8. Display coverage summary
- **Fails if**: Any test fails
- **Artifacts**: HTML coverage report (downloadable for 30 days)

##### **Job 3: `validate-airflow`** - Validate Airflow DAGs
- **Purpose**: Check if Airflow DAGs are valid
- **Steps**:
  1. Checkout code
  2. Set up Python 3.9
  3. Install Apache Airflow
  4. Validate DAG syntax and check for import errors
- **Fails if**: DAG has syntax errors or import issues

#### **Job Execution:**
- All jobs run **in parallel** (they don't depend on each other)
- If any job fails, the entire CI pipeline is marked as failed

---

### **CD Pipeline** (`deploy.yml`)

#### **Triggers:**
```yaml
on:
  push:
    branches: [ main ]              # Runs only on push to main branch
  workflow_dispatch:                # Can be manually triggered from GitHub UI
```

**Runs on:**
- Push to `main` branch only
- Manual trigger (via GitHub Actions UI)

#### **Job: `deploy`** - Deploy to GCP

##### **Step 1: Checkout code**
- Downloads code from repository

##### **Step 2: Authenticate to Google Cloud**
- Uses service account key from GitHub Secrets
- Authenticates with GCP

##### **Step 3: Set up Cloud SDK**
- Installs gcloud CLI tools
- Sets GCP project

##### **Step 4: Verify GCS bucket exists**
- Checks if the bucket exists
- **Fails if**: Bucket doesn't exist

##### **Step 5: Upload Spark jobs to GCS**
- Uploads all Python files from `spark/jobs/` to `gs://bucket-name/spark-jobs/`
- Uses parallel upload (`-m` flag) for faster upload

##### **Step 6: Upload BigQuery connector JAR**
- Checks if BigQuery connector JAR exists in GCS
- Downloads and uploads it if missing

##### **Step 7: Upload Airflow DAGs to Composer**
- Gets Composer environment bucket path
- Uploads DAGs from `airflow/dags/` to Composer's DAG folder
- **Warning only** if Composer not found (doesn't fail)

##### **Step 8: Verify Dataproc cluster**
- Checks if Dataproc cluster exists and is accessible
- **Warning only** if cluster not found (doesn't fail)

##### **Step 9: Verify BigQuery dataset**
- Checks if BigQuery dataset exists
- Creates dataset if it doesn't exist

##### **Step 10: Enable required APIs**
- Enables Cloud Build, Cloud Run, Artifact Registry APIs
- Required for Cloud Run deployment

##### **Step 11: Get or create service account**
- Uses custom service account if provided (via `CLOUD_RUN_SA_EMAIL` secret)
- Otherwise uses default compute service account
- Grants BigQuery permissions automatically

##### **Step 12: Create Artifact Registry repository**
- Creates Docker repository for storing container images
- Only creates if it doesn't exist

##### **Step 13: Build and push Docker image**
- Builds Docker image using Cloud Build
- Pushes image to Artifact Registry
- Tags image with commit SHA for versioning

##### **Step 14: Deploy to Cloud Run**
- Creates Cloud Run service if it doesn't exist
- Updates existing service if it exists
- Configures:
  - Public access (globally accessible)
  - Memory: 512Mi
  - CPU: 1
  - Max instances: 10
  - Timeout: 300 seconds
  - Environment variables (GCP_PROJECT_ID, BIGQUERY_DATASET)

##### **Step 15: Get service URL**
- Retrieves the deployed Cloud Run service URL
- This URL is globally accessible

##### **Step 16: Verify deployment**
- Tests the health endpoint to ensure deployment is successful
- Verifies API is responding correctly

##### **Step 17: Deployment summary**
- Displays summary of what was deployed
- Shows Cloud Run API URL and endpoints
- Shows next steps for users

---

## 🔄 Workflow Flow Diagram

```
Developer pushes code
        │
        ├─── Push to main/dev? ─────────┐
        │                               │
        └─── Open/Update PR? ───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   CI Pipeline Runs    │
        └───────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
   ┌────────┐          ┌──────────────┐
   │  Lint  │          │ Test Spark   │
   └────────┘          └──────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │ Validate Airflow DAGs│
        └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │  All checks pass?    │
        └──────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
     ❌ Fail              ✅ Pass
        │                       │
        │                       ▼
        │              ┌──────────────────┐
        │              │ Push to main?    │
        │              └──────────────────┘
        │                       │
        │                       ▼
        │              ┌──────────────────┐
        │              │  CD Pipeline     │
        │              │     Runs         │
        │              └──────────────────┘
        │                       │
        │                       ▼
        │              ┌──────────────────┐
        │              │ Deploy to GCP    │
        │              │ - Upload Spark   │
        │              │ - Upload DAGs    │
        │              │ - Deploy API     │
        │              │   to Cloud Run   │
        │              │ - Verify Resources│
        │              └──────────────────┘
        │
        └─── PR blocked or workflow failed
```

---

## 📊 Key Differences

| Feature | CI Pipeline | CD Pipeline |
|---------|-------------|-------------|
| **Purpose** | Test & Validate | Deploy |
| **Triggers** | Push + PR | Push to main only |
| **Runs Jobs** | 3 jobs (parallel) | 1 job |
| **Requires GCP Auth** | ❌ No | ✅ Yes |
| **Uploads to GCP** | ❌ No | ✅ Yes |
| **Deploys API** | ❌ No | ✅ Yes (Cloud Run) |
| **Fails on** | Test failures, lint errors | Missing bucket, auth failures, deployment errors |

---

## 🔧 Configuration Requirements

### **CI Pipeline:**
- No secrets required
- Uses public GitHub Actions runners

### **CD Pipeline:**
Requires GitHub Secrets:
- `GCP_SA_KEY`: Service account JSON key (required)
- `GCP_PROJECT_ID`: GCP project ID (required)

Optional GitHub Secrets (with defaults):
- `GCS_BUCKET_NAME`: GCS bucket name (defaults to 'ride-analytics')
- `DATAPROC_CLUSTER_NAME`: Dataproc cluster name (defaults to 'hadoop-dev-new')
- `COMPOSER_ENVIRONMENT`: Composer environment name (defaults to 'airflow-dev')
- `COMPOSER_REGION`: Composer region (defaults to 'us-central1')
- `CLOUD_RUN_SERVICE_NAME`: Cloud Run service name (defaults to 'ride-analytics-api')
- `CLOUD_RUN_REGION`: Cloud Run region (defaults to 'us-central1')
- `CLOUD_RUN_SA_EMAIL`: Custom service account email for Cloud Run (optional, uses default if not provided)
- `BIGQUERY_DATASET`: BigQuery dataset name (defaults to 'ridesharing_analytics')

**Service Account Permissions Required:**
The service account used (`GCP_SA_KEY`) needs these roles:
- Cloud Build Service Account
- Cloud Run Admin
- Artifact Registry Writer
- IAM Security Admin (for granting BigQuery permissions)
- Storage Object Admin (for GCS uploads)
- BigQuery Data Editor (for dataset creation)

---

## 📝 Typical Workflow

### **Scenario 1: Developer pushes feature branch**
1. Developer creates feature branch and pushes code
2. CI Pipeline runs automatically
3. Developer sees test results in GitHub
4. If tests pass, developer creates PR
5. CI Pipeline runs again on PR
6. After PR review and merge to `main`:
   - CI Pipeline runs again
   - CD Pipeline runs automatically
   - Code is deployed to GCP

### **Scenario 2: Direct push to main**
1. Developer pushes directly to `main` branch
2. CI Pipeline runs (tests, linting)
3. If CI passes, CD Pipeline runs automatically
4. Code is deployed to GCP

### **Scenario 3: Manual deployment**
1. Developer goes to GitHub Actions tab
2. Selects "CD Pipeline"
3. Clicks "Run workflow"
4. CD Pipeline runs and deploys code

---

## 🎯 Best Practices

1. **Always run CI before CD**: CI Pipeline validates code before deployment
2. **Don't skip CI**: Even for hotfixes, let CI run first
3. **Check artifacts**: Download coverage reports to see test coverage
4. **Monitor deployments**: Check deployment summary for any warnings
5. **Use PRs**: Create pull requests to trigger CI before merging

---

## 🐛 Troubleshooting

### **CI Pipeline fails:**
- Check test logs in GitHub Actions
- Download coverage report to see which tests failed
- Fix linting errors locally before pushing

### **CD Pipeline fails:**
- Check if GCP service account has correct permissions
- Verify bucket exists: `gsutil ls gs://your-bucket-name`
- Check if Composer environment exists
- Verify all GitHub Secrets are set correctly

### **CD Pipeline warnings (but doesn't fail):**
- Composer not found: Create Composer environment or upload DAGs manually
- Dataproc cluster not found: Ensure cluster is created and running
- BigQuery dataset not found: Will be created automatically

### **Cloud Run Deployment:**
- **Service URL**: Check deployment summary for the global API URL
- **API Documentation**: Access at `{SERVICE_URL}/docs`
- **Health Check**: Test at `{SERVICE_URL}/api/health`
- **Permissions**: Ensure service account has BigQuery access
- **Logs**: View logs in Cloud Run console or using `gcloud run services logs read`

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GCP GitHub Actions](https://github.com/google-github-actions)
- Check workflow runs in: Repository → Actions tab

