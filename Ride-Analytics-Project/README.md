# Ride-Sharing Analytics Pipeline

## 📋 Project Overview

A production-ready data engineering pipeline for processing ride-sharing data (Uber/Lyft-style) with comprehensive monitoring, data quality checks, and automated deployment. This project demonstrates real-world data engineering practices on Google Cloud Platform.

**Domain**: Ride-Sharing & Transportation Analytics  
**Complexity**: Medium to Advanced  
**Focus**: Production-grade pipeline with observability, testing, and CI/CD

---

## 🎯 Business Use Case

Process daily ride-sharing transactions to generate:
- **Ride Analytics**: Total rides, revenue, average ride duration
- **Driver Performance**: Driver ratings, earnings, trip completion rate
- **Demand Patterns**: Peak hours, popular routes, surge pricing analysis
- **Passenger Insights**: Ride frequency, preferred locations, spending patterns
- **Real-time API**: FastAPI service for querying ride analytics and metrics

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   Data Sources  │
│  (CSV/JSON)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   GCS Bucket (ride-analytics)      │
│   ┌─────────────────────────────┐   │
│   │ bronze/                     │   │  ◄─── Raw Data
│   │   ├── drivers/              │   │
│   │   ├── passengers/           │   │
│   │   └── rides/YYYY-MM-DD/     │   │
│   │ silver/                     │   │  ◄─── Processed Data
│   │   └── rides_processed/      │   │
│   │ spark-jobs/                 │   │  ◄─── Spark Scripts
│   │   ├── bronze_to_silver.py   │   │
│   │   ├── data_quality.py       │   │
│   │   └── silver_to_gold.py     │   │
│   │ quality-reports/            │   │  ◄─── Quality Reports
│   │   └── YYYY-MM-DD/           │   │
│   └─────────────────────────────┘   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Apache Airflow │  ◄─── Orchestration & Scheduling
│   (Composer)    │
└────────┬────────┘
         │
         ├─────────────────┐
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  Data Quality   │  │  PySpark Jobs   │
│     Checks      │  │  (Dataproc)     │
└────────┬────────┘  └────────┬────────┘
         │                    │
         └────────┬───────────┘
                  ▼
         ┌─────────────────┐
         │    BigQuery     │  ◄─── Analytics Tables (Gold)
         │  (Data Warehouse)│
         └─────────────────┘
```

---

## 📊 Data Flow

### 1. **Data Ingestion (Bronze Layer)**
- **Source**: Daily CSV/JSON files (rides, drivers, passengers)
- **Destination**: Single GCS Bucket with folders (`gs://ride-analytics/bronze/`)
  - `bronze/drivers/drivers.csv`
  - `bronze/passengers/passengers.csv`
  - `bronze/rides/YYYY-MM-DD/rides.csv`
- **Process**: Airflow DAG triggers on schedule, uploads raw files
- **Format**: Preserve original format with metadata (timestamp, source)

### 2. **Data Quality Checks**
- **Framework**: Great Expectations or custom PySpark validations
- **Checks**:
  - Schema validation
  - Null checks on critical fields (ride_id, driver_id, passenger_id)
  - Data type validation
  - Business rule validation (e.g., ride_fare > 0, distance > 0, duration > 0)
  - Geographic validation (valid lat/long coordinates)
  - Duplicate detection
- **Action**: Fail pipeline if quality checks fail, send alerts

### 3. **Data Processing (Silver Layer)**
- **Engine**: PySpark on Dataproc
- **Transformations**:
  - Data cleaning and standardization
  - Join operations (rides + drivers + passengers)
  - Calculate derived fields:
    - Ride distance (Haversine formula for pickup/dropoff coordinates)
    - Ride duration (from timestamps)
    - Fare per mile/km
    - Surge multiplier impact
  - Geospatial enrichment (city, zone from coordinates)
  - Time-based features (hour, day_of_week, is_peak_hour)
- **Output**: Parquet files in GCS (`gs://ride-analytics/silver/`)
  - `silver/rides_processed/`
  - `silver/drivers_processed/`
  - `silver/passengers_processed/`
- **Partitioning**: By date (year/month/day)

### 4. **Data Warehouse (Gold Layer)**
- **Destination**: BigQuery
- **Tables**:
  - `fact_rides` - Ride transactions
  - `dim_drivers` - Driver master (SCD Type 2)
  - `dim_passengers` - Passenger master (SCD Type 2)
  - `agg_daily_rides` - Daily ride aggregations
  - `agg_driver_performance` - Driver analytics (ratings, earnings, trips)
  - `agg_demand_patterns` - Hourly/daily demand by location
  - `agg_revenue_metrics` - Revenue analytics by time and location

### 5. **API Layer (FastAPI) - Local Development Only**
- **Purpose**: Serve processed ride analytics via REST API (local development/testing)
- **Endpoints**:
  - `/api/rides/daily` - Get daily ride metrics (count, revenue, avg duration)
  - `/api/drivers/{driver_id}` - Get driver performance and earnings
  - `/api/passengers/{passenger_id}` - Get passenger ride history
  - `/api/demand/peak-hours` - Get peak demand hours by location
  - `/api/revenue/summary` - Get revenue summary by date range
  - `/api/health` - Health check endpoint
- **Deployment**: Local development only (not deployed via CI/CD)

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | Apache Airflow (Cloud Composer) | Workflow scheduling & dependency management |
| **Processing** | PySpark (Dataproc) | Distributed data transformation |
| **Storage** | GCS Bucket (single bucket with folders) | Data lake (Bronze/Silver layers) |
| **Warehouse** | BigQuery | Analytics & reporting |
| **API** | FastAPI (Local only) | Data serving layer (local development) |
| **Monitoring** | Cloud Monitoring + Cloud Logging | Pipeline observability |
| **Alerting** | Cloud Monitoring Alerts → Email/PagerDuty | Failure notifications |
| **CI/CD** | GitHub Actions | Automated testing & deployment |
| **Testing** | pytest + PySpark Testing | Unit & integration tests |
| **Data Quality** | Great Expectations / Custom | Data validation framework |

---

## 📁 Project Structure

```
Ride-Analytics-Project/
├── README.md                       # Project overview and architecture
├── SETUP.md                        # Setup and deployment guide
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI pipeline (tests, linting)
│       └── deploy.yml             # CD pipeline (deploy to GCP)
├── airflow/
│   ├── dags/
│   │   └── rides_pipeline_dag.py  # Main Airflow DAG
│   └── requirements.txt
├── spark/
│   ├── jobs/
│   │   ├── bronze_to_silver.py    # Spark transformation job
│   │   ├── silver_to_gold.py      # BigQuery load job
│   │   └── data_quality.py        # Data quality checks
│   ├── tests/
│   │   └── test_transformations.py
│   └── requirements.txt
├── api/
│   ├── main.py                    # FastAPI application (3 endpoints)
│   ├── Dockerfile                 # Container definition
│   └── requirements.txt
└── scripts/
    ├── generate_sample_data.py    # Realistic data generation
    ├── requirements.txt
    └── data/                      # Generated sample data (gitignored)
        └── raw/
```

---

## 🔄 Pipeline Process Flow

### Daily Execution Flow

1. **00:00 UTC - Data Arrival**
   - New ride data files arrive in source system
   - Airflow DAG triggers automatically

2. **00:05 UTC - Data Ingestion (Bronze)**
   - Airflow task: `ingest_raw_data`
   - Upload ride/driver/passenger files to GCS Bronze bucket
   - Log ingestion metadata

3. **00:10 UTC - Data Quality Validation**
   - Airflow task: `run_data_quality_checks`
   - Execute PySpark data quality job
   - Validate schema, nulls, business rules, geospatial data
   - **If FAIL**: Send alert, stop pipeline
   - **If PASS**: Continue to processing

4. **00:20 UTC - Data Processing (Silver)**
   - Airflow task: `process_silver_layer`
   - Submit PySpark job to Dataproc
   - Transform and clean data
   - Calculate distances, durations, fare metrics
   - Enrich with geospatial and time features
   - Write to GCS Silver bucket (Parquet)

5. **00:40 UTC - Load to BigQuery (Gold)**
   - Airflow task: `load_to_bigquery`
   - Load Parquet files to BigQuery tables
   - Update dimension tables (SCD Type 2 for drivers/passengers)
   - Create aggregated tables (daily rides, driver performance, demand patterns)

6. **00:50 UTC - Post-Processing**
   - Airflow task: `update_api_cache`
   - Refresh FastAPI cache (if needed)
   - Send success notification

---

## 🔍 Data Quality Framework

### Validation Rules

1. **Schema Validation**
   - Required columns present
   - Data types match schema
   - No unexpected columns

2. **Completeness Checks**
   - No nulls in critical fields (ride_id, driver_id, passenger_id, fare)
   - Minimum row count threshold

3. **Business Rule Validation**
   - Ride fare > 0
   - Ride distance > 0
   - Ride duration > 0
   - Pickup/dropoff coordinates within valid range (-90 to 90 for lat, -180 to 180 for long)
   - Ride date within valid range
   - Driver rating between 1-5 (if applicable)

4. **Uniqueness Checks**
   - No duplicate ride_ids
   - Primary key constraints

5. **Referential Integrity**
   - All driver_ids exist in driver table
   - All passenger_ids exist in passenger table

6. **Geospatial Validation**
   - Valid latitude/longitude coordinates
   - Pickup and dropoff locations are different
   - Distance calculation is reasonable

### Quality Metrics Tracked
- Total records processed
- Records passed/failed validation
- Data quality score (%)
- Processing time
- Error details

---

## 📈 Monitoring & Observability

### Cloud Monitoring Metrics

1. **Pipeline Metrics**
   - DAG execution status (success/failure)
   - Job execution time
   - Records processed per run
   - Data quality score

2. **Infrastructure Metrics**
   - Dataproc cluster CPU/Memory usage
   - GCS storage usage
   - BigQuery query performance
   - Cloud Run API latency

3. **Business Metrics**
   - Daily ride volume
   - Daily revenue
   - Average ride duration
   - Data freshness (last successful run)
   - API request count

### Alerting Strategy

**Critical Alerts** (PagerDuty/Email):
- Pipeline failure (DAG failed)
- Data quality check failure
- Dataproc cluster down
- BigQuery load failure
- API service down

**Warning Alerts** (Email):
- Pipeline running longer than expected
- Data quality score below threshold
- High error rate in API
- Storage usage > 80%

### Logging
- All pipeline steps log to Cloud Logging
- Structured logging with correlation IDs
- Error stack traces captured
- Performance metrics logged

---

## 🚨 Failure & Recovery

### Failure Scenarios & Recovery

1. **Data Quality Failure**
   - **Detection**: Data quality job returns failure
   - **Action**: Stop pipeline, send alert
   - **Recovery**: Manual investigation, fix data source, re-run DAG

2. **Dataproc Job Failure**
   - **Detection**: Spark job returns non-zero exit code
   - **Action**: Airflow retry (3 attempts with backoff)
   - **Recovery**: Auto-retry, if fails → alert, manual intervention

3. **BigQuery Load Failure**
   - **Detection**: Load job fails
   - **Action**: Retry with exponential backoff
   - **Recovery**: Check GCS files, validate schema, re-run

4. **Airflow DAG Failure**
   - **Detection**: Task failure after retries
   - **Action**: Send alert, mark DAG as failed
   - **Recovery**: Manual DAG re-run from failed task

5. **API Service Failure**
   - **Detection**: Health check endpoint fails
   - **Action**: Cloud Run auto-restart, alert if persistent
   - **Recovery**: Check logs, redeploy if needed

### Idempotency
- All jobs are idempotent (can re-run safely)
- Use date partitions to avoid duplicate processing
- Upsert logic in BigQuery (merge statements)

---

## 🧪 Testing Strategy

### Unit Tests (PySpark)
- Test individual transformation functions
- Mock Spark DataFrames
- Test data quality validation logic
- Test edge cases (nulls, empty data)

### Integration Tests
- Test end-to-end pipeline with sample data
- Test Airflow DAG with test environment

### Test Coverage
- Target: 80%+ code coverage
- Focus on business logic and transformations
- Test error handling paths

### CI/CD Testing
- Run tests on every PR
- Run integration tests before deployment
- Fail build if tests fail

---

## 🔄 CI/CD Pipeline (GitHub Actions)

This project has two GitHub Actions workflows. See [`.github/workflows/README.md`](.github/workflows/README.md) for detailed explanation.

### Quick Overview:

#### **1. CI Pipeline** (`ci.yml`) - Continuous Integration
**Triggers:** Every push and pull request

**Jobs (run in parallel):**
- ✅ **Lint** - Check code quality (flake8, black)
- ✅ **Test Spark** - Run PySpark unit tests with coverage
- ✅ **Validate Airflow** - Check DAG syntax

**Purpose:** Validate code quality before merging/deployment

#### **2. CD Pipeline** (`deploy.yml`) - Continuous Deployment
**Triggers:** Push to `main` branch or manual trigger

**Steps:**
1. Authenticate to GCP
2. Upload Spark jobs to GCS (`gs://bucket/spark-jobs/`)
3. Upload Airflow DAGs to Composer
4. Verify GCP resources (bucket, Dataproc, BigQuery)

**Purpose:** Deploy code to GCP automatically

### Workflow Flow:
```
Push Code → CI Pipeline Runs → Tests Pass? → Merge to main → CD Pipeline Runs → Deployed to GCP
                ↓
           Tests Fail? → Fix Issues → Push Again
```

**Note:** 
- CI runs on every push/PR (validates code)
- CD runs only on `main` branch (deploys code)

**For detailed explanation:** See [`.github/workflows/README.md`](.github/workflows/README.md)

---

## 🚀 FastAPI Integration (Local Development & Cloud Run)

**Note:** FastAPI is deployed to Cloud Run for global API access. It can also be run locally for development and testing.

### Purpose
- Serve processed analytics data via REST API
- Real-time querying of BigQuery results
- Lightweight, fast data access layer

### Key Endpoints

```
GET /api/health
  - Health check endpoint
  - Returns service status

GET /api/rides/daily?date=2025-01-15
  - Get daily ride metrics
  - Returns: total_rides, total_revenue, avg_duration, avg_distance

GET /api/drivers/{driver_id}
  - Get driver performance and earnings
  - Returns: driver info, total_trips, total_earnings, avg_rating, completion_rate

GET /api/passengers/{passenger_id}
  - Get passenger ride history
  - Returns: passenger info, ride_history, total_spent, favorite_locations

GET /api/demand/peak-hours?date=2025-01-15&location=city_center
  - Get peak demand hours by location
  - Returns: hour, ride_count, avg_surge_multiplier

GET /api/revenue/summary?start_date=2025-01-01&end_date=2025-01-31
  - Get revenue summary by date range
  - Returns: total_revenue, ride_count, avg_fare, revenue_by_day

GET /api/metrics/pipeline
  - Get pipeline execution metrics
  - Returns: last_run_time, status, records_processed
```

### Implementation
- FastAPI framework
- BigQuery client for data queries
- Response caching (Redis or in-memory)
- Authentication (API keys or OAuth)
- Rate limiting

---

## 📋 Data Schema

### Bronze Layer (Raw Data)

**rides.csv**
```
ride_id, driver_id, passenger_id, pickup_datetime, dropoff_datetime, 
pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude, 
fare_amount, tip_amount, surge_multiplier, ride_status
```

**drivers.csv**
```
driver_id, name, email, phone, registration_date, vehicle_type, 
license_plate, city, rating, is_active
```

**passengers.csv**
```
passenger_id, name, email, phone, registration_date, city, 
preferred_payment_method, rating
```

### Silver Layer (Processed)

**rides_processed** (Parquet)
- All bronze fields + calculated fields
- ride_distance_km, ride_duration_minutes, fare_per_km
- pickup_city, dropoff_city, pickup_zone, dropoff_zone
- pickup_hour, pickup_day_of_week, is_peak_hour
- Data types standardized
- Nulls handled

### Gold Layer (BigQuery)

**fact_rides**
- Ride transaction facts
- Partitioned by pickup_date
- Clustered by driver_id

**dim_drivers** (SCD Type 2)
- Driver dimension with history
- effective_date, end_date, is_current

**dim_passengers** (SCD Type 2)
- Passenger dimension with history
- effective_date, end_date, is_current

**agg_daily_rides**
- Daily aggregated rides
- total_rides, total_revenue, avg_duration, avg_distance

**agg_driver_performance**
- Driver performance metrics
- total_trips, total_earnings, avg_rating, completion_rate

**agg_demand_patterns**
- Demand patterns by hour and location
- ride_count, avg_surge_multiplier, peak_hours

---

## 🎓 Learning Objectives

By completing this project, you will learn:

1. **GCP Services**
   - Cloud Composer (Airflow)
   - Dataproc (Spark)
   - GCS (Storage)
   - BigQuery (Data Warehouse)
   - FastAPI (Local development only)
   - Cloud Monitoring (Observability)

2. **Data Engineering Patterns**
   - Medallion architecture (Bronze/Silver/Gold)
   - SCD Type 2 implementation
   - Data quality framework
   - Idempotent pipelines

3. **Production Practices**
   - Pipeline monitoring & alerting
   - Failure handling & recovery
   - CI/CD automation
   - Unit testing for data pipelines
   - API development for data access

4. **Best Practices**
   - Code organization
   - Configuration management
   - Error handling
   - Logging & observability
   - Documentation

---

## 📝 Next Steps

1. **Ensure GCP Resources are Ready**
   - Single GCS bucket: `ride-analytics` (with bronze/, silver/, spark-jobs/ folders)
   - Cloud Composer environment
   - Managed Dataproc cluster (already running)
   - BigQuery dataset

2. **Implement Data Pipeline**
   - Create Airflow DAGs
   - Develop Spark transformation jobs
   - Implement data quality checks
   - Build BigQuery tables

3. **Develop FastAPI Service** (Optional - Local development only)
   - Create API endpoints
   - Integrate with BigQuery
   - Deploy separately when needed

4. **Setup Monitoring**
   - Configure Cloud Monitoring
   - Create alerting policies
   - Build dashboards

5. **Implement CI/CD**
   - Setup GitHub Actions
   - Write unit tests
   - Configure deployment pipeline

---

## 🔧 Prerequisites

- Google Cloud Platform account
- GCP project with billing enabled
- Python 3.9+
- GitHub account
- Basic knowledge of:
  - Apache Airflow
  - PySpark
  - BigQuery
  - FastAPI
  - Git & GitHub Actions

---

## 📚 Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Cloud Monitoring](https://cloud.google.com/monitoring/docs)

---

## 📖 Documentation

- **README.md** - This file (project overview and architecture)
- **SETUP.md** - Step-by-step setup and deployment guide

---

**Status**: Ready for Deployment  
**Last Updated**: 2025-01-15

