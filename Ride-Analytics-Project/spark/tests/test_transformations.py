"""
Unit tests for Spark transformation jobs
Make Sure to install these python package
pip install pytest pytest-cov
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from pyspark.sql.functions import col
from datetime import datetime
import sys
import os

# Set Python path for Spark workers to match driver
# This ensures both driver and workers use the same Python version
python_exec = sys.executable
os.environ['PYSPARK_PYTHON'] = python_exec
os.environ['PYSPARK_DRIVER_PYTHON'] = python_exec

# Add parent directories to path so we can import from jobs module
# Test is in spark/tests/, so we need to go up to spark/, then up to project root
spark_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root = os.path.abspath(os.path.join(spark_dir, '..'))
sys.path.insert(0, project_root)

# Import from spark.jobs module (this matches how it would work in production)
from spark.jobs.bronze_to_silver import haversine_distance, transform_rides


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing"""
    import zipfile
    import tempfile
    
    # Ensure Python version consistency
    os.environ['PYSPARK_PYTHON'] = sys.executable
    os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
    
    # Get directory paths
    spark_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    project_root = os.path.abspath(os.path.join(spark_dir, '..'))
    jobs_dir = os.path.join(spark_dir, 'jobs')
    
    # Add project root to PYTHONPATH for driver
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if current_pythonpath:
        os.environ['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
    else:
        os.environ['PYTHONPATH'] = project_root
    
    spark = SparkSession.builder \
        .appName("TestTransformations") \
        .master("local[2]") \
        .config("spark.sql.adaptive.enabled", "false") \
        .config("spark.python.worker.reuse", "false") \
        .config("spark.executorEnv.PYTHONPATH", project_root) \
        .getOrCreate()
    
    # Create a zip file of the spark directory and add it to Spark
    # This ensures workers can import spark.jobs.bronze_to_silver
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
        zip_path = tmp_zip.name
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all Python files from spark directory
            for root, dirs, files in os.walk(spark_dir):
                # Skip __pycache__ directories
                dirs[:] = [d for d in dirs if d != '__pycache__']
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        # Archive path should maintain directory structure
                        arcname = os.path.relpath(file_path, project_root)
                        zipf.write(file_path, arcname)
        
        # Add the zip file to Spark so workers can import from it
        spark.sparkContext.addPyFile(zip_path)
    
    yield spark
    spark.stop()
    
    # Clean up temporary zip file
    try:
        os.unlink(zip_path)
    except:
        pass


@pytest.fixture
def sample_rides_data(spark):
    """Create sample rides DataFrame"""
    schema = StructType([
        StructField("ride_id", StringType(), True),
        StructField("driver_id", StringType(), True),
        StructField("passenger_id", StringType(), True),
        StructField("pickup_datetime", StringType(), True),
        StructField("dropoff_datetime", StringType(), True),
        StructField("pickup_latitude", StringType(), True),
        StructField("pickup_longitude", StringType(), True),
        StructField("dropoff_latitude", StringType(), True),
        StructField("dropoff_longitude", StringType(), True),
        StructField("fare_amount", StringType(), True),
        StructField("tip_amount", StringType(), True),
        StructField("surge_multiplier", StringType(), True),
        StructField("ride_status", StringType(), True),
    ])
    
    data = [
        ("RIDE001", "DRV001", "PAS001", "2025-01-15 10:00:00", "2025-01-15 10:30:00",
         "37.7749", "-122.4194", "37.7849", "-122.4294", "25.50", "5.00", "1.0", "completed"),
        ("RIDE002", "DRV002", "PAS002", "2025-01-15 11:00:00", "2025-01-15 11:20:00",
         "37.7750", "-122.4195", "37.7850", "-122.4295", "20.00", "0.00", "1.5", "completed"),
    ]
    
    return spark.createDataFrame(data, schema)


def test_haversine_distance():
    """Test Haversine distance calculation"""
    # San Francisco to Oakland (approximately 13 km)
    lat1, lon1 = 37.7749, -122.4194
    lat2, lon2 = 37.8044, -122.2711
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    assert distance is not None
    assert 10 < distance < 20  # Should be around 13 km


def test_haversine_distance_invalid():
    """Test Haversine distance with invalid inputs"""
    distance = haversine_distance(None, None, None, None)
    assert distance is None


def test_transform_rides(spark, sample_rides_data):
    """Test rides transformation"""
    from spark.jobs.bronze_to_silver import transform_rides
    
    transformed_df = transform_rides(spark, sample_rides_data)
    
    # Check that new columns are created
    assert "ride_distance_km" in transformed_df.columns
    assert "ride_duration_minutes" in transformed_df.columns
    assert "fare_per_km" in transformed_df.columns
    assert "total_fare" in transformed_df.columns
    assert "pickup_hour" in transformed_df.columns
    assert "pickup_day_of_week" in transformed_df.columns
    assert "is_peak_hour" in transformed_df.columns
    
    # Check data types
    assert transformed_df.schema["ride_distance_km"].dataType == DoubleType()
    assert transformed_df.schema["total_fare"].dataType == DoubleType()
    
    # Check that records are processed
    assert transformed_df.count() == 2


def test_transform_rides_with_nulls(spark):
    """Test rides transformation with null values"""
    from spark.jobs.bronze_to_silver import transform_rides
    
    schema = StructType([
        StructField("ride_id", StringType(), True),
        StructField("driver_id", StringType(), True),
        StructField("passenger_id", StringType(), True),
        StructField("pickup_datetime", StringType(), True),
        StructField("dropoff_datetime", StringType(), True),
        StructField("pickup_latitude", StringType(), True),
        StructField("pickup_longitude", StringType(), True),
        StructField("dropoff_latitude", StringType(), True),
        StructField("dropoff_longitude", StringType(), True),
        StructField("fare_amount", StringType(), True),
        StructField("tip_amount", StringType(), True),
        StructField("surge_multiplier", StringType(), True),
        StructField("ride_status", StringType(), True),
    ])
    
    data = [
        ("RIDE001", "DRV001", "PAS001", "2025-01-15 10:00:00", None,
         None, None, None, None, None, None, "1.0", "cancelled"),
    ]
    
    df = spark.createDataFrame(data, schema)
    transformed_df = transform_rides(spark, df)
    
    # Should handle nulls gracefully
    assert transformed_df.count() == 1
    assert transformed_df.filter(col("ride_distance_km").isNull()).count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

