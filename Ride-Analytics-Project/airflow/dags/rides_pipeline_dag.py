"""
Ride-Sharing Analytics Pipeline DAG
Orchestrates the complete data pipeline from Bronze to Gold
"""

from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocSubmitJobOperator
)
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os
from airflow.models import Variable

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# GCP Configuration
PROJECT_ID = Variable.get('GCP_PROJECT_ID', default_var='dev-sunset-468907-e9')
REGION = Variable.get('GCP_REGION', default_var='us-central1')
CLUSTER_NAME = Variable.get('DATAPROC_CLUSTER_NAME', default_var='hadoop-dev-new')
BUCKET_NAME = Variable.get('GCS_BUCKET_NAME', default_var='ride-analytics')  # Single bucket for all data
DATASET = Variable.get('BIGQUERY_DATASET', default_var='ridesharing_analytics')



# Note: All Spark jobs are in gs://{BUCKET_NAME}/spark-jobs/
# All data is in gs://{BUCKET_NAME}/bronze/ and gs://{BUCKET_NAME}/silver/

# DAG definition
with DAG(
    'rides_pipeline_dag',
    default_args=default_args,
    description='Ride-Sharing Analytics Pipeline',
    schedule_interval='0 0 * * *',  # Daily at midnight UTC
    start_date=days_ago(1),
    catchup=False,
    tags=['ridesharing', 'analytics', 'gcp'],
) as dag:

    # Task 1: Check if data exists in Bronze folder
    check_bronze_data = GCSListObjectsOperator(
        task_id='check_bronze_data',
        bucket=BUCKET_NAME,
        prefix='bronze/rides/',
        gcp_conn_id='google_cloud_default',
    )

    # Task 2: Run Data Quality Checks
    # Note: Using existing managed Dataproc cluster
    run_data_quality = DataprocSubmitJobOperator(
        task_id='run_data_quality',
        job={
            'reference': {'project_id': PROJECT_ID},
            'placement': {'cluster_name': CLUSTER_NAME},
            'pyspark_job': {
                'main_python_file_uri': f'gs://{BUCKET_NAME}/spark-jobs/data_quality.py',
                'args': [
                    f'gs://{BUCKET_NAME}/bronze',
                    f'gs://{BUCKET_NAME}/quality-reports/{{{{ ds }}}}',
                ],
                'python_file_uris': [],
                'jar_file_uris': [],
            }
        },
        region=REGION,
        project_id=PROJECT_ID,
    )

    # Task 4: Bronze to Silver Transformation
    bronze_to_silver = DataprocSubmitJobOperator(
        task_id='bronze_to_silver',
        job={
            'reference': {'project_id': PROJECT_ID},
            'placement': {'cluster_name': CLUSTER_NAME},
            'pyspark_job': {
                'main_python_file_uri': f'gs://{BUCKET_NAME}/spark-jobs/bronze_to_silver.py',
                'args': [
                    f'gs://{BUCKET_NAME}/bronze',
                    f'gs://{BUCKET_NAME}/silver',
                    '{{ ds }}',  # Processing date from Airflow
                ],
                'python_file_uris': [],
                'jar_file_uris': [],
            }
        },
        region=REGION,
        project_id=PROJECT_ID,
    )

    # Task 4: Silver to Gold (BigQuery Load)
    silver_to_gold = DataprocSubmitJobOperator(
        task_id='silver_to_gold',
        job={
            'reference': {'project_id': PROJECT_ID},
            'placement': {'cluster_name': CLUSTER_NAME},
            'pyspark_job': {
                'main_python_file_uri': f'gs://{BUCKET_NAME}/spark-jobs/silver_to_gold.py',
                'args': [
                    f'gs://{BUCKET_NAME}/silver',
                    PROJECT_ID,
                    DATASET,
                    BUCKET_NAME,  # Temp bucket for BigQuery
                    '{{ ds }}',  # Processing date
                ],
                'python_file_uris': [],
                'jar_file_uris': [],
            }
        },
        region=REGION,
        project_id=PROJECT_ID,
    )

    # Define task dependencies
    # Note: Using existing managed Dataproc cluster (no create/delete operations)
    check_bronze_data >> run_data_quality >> bronze_to_silver >> silver_to_gold

