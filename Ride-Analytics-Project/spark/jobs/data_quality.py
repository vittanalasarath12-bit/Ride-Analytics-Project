"""
Data Quality Check Job
Validates data quality and generates quality report
"""

import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    isnan,
    isnull,
    sum as spark_sum,
    when,
)
from datetime import datetime


def check_schema(df, required_columns):
    """Check if required columns exist"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


def check_nulls(df, critical_columns):
    """Check for nulls in critical columns"""
    null_counts = {}
    total_rows = df.count()

    for col_name in critical_columns:
        if col_name in df.columns:
            null_count = df.filter(
                col(col_name).isNull() | isnan(col(col_name))
            ).count()
            null_percentage = (null_count / total_rows * 100) if total_rows > 0 else 0
            null_counts[col_name] = {
                "null_count": null_count,
                "null_percentage": round(null_percentage, 2),
                "total_rows": total_rows,
            }

    return null_counts


def check_business_rules_rides(df):
    """Check business rules for rides data"""
    total_rows = df.count()
    issues = {}

    # Check fare_amount > 0
    if "fare_amount" in df.columns:
        invalid_fares = df.filter(
            (col("fare_amount").isNull()) | (col("fare_amount") <= 0)
        ).count()
        issues["fare_amount_positive"] = {
            "invalid_count": invalid_fares,
            "invalid_percentage": (
                round(invalid_fares / total_rows * 100, 2) if total_rows > 0 else 0
            ),
        }

    # Check valid coordinates
    if all(col in df.columns for col in ["pickup_latitude", "pickup_longitude"]):
        invalid_coords = df.filter(
            (col("pickup_latitude").isNull())
            | (col("pickup_latitude") < -90)
            | (col("pickup_latitude") > 90)
            | (col("pickup_longitude").isNull())
            | (col("pickup_longitude") < -180)
            | (col("pickup_longitude") > 180)
        ).count()
        issues["valid_coordinates"] = {
            "invalid_count": invalid_coords,
            "invalid_percentage": (
                round(invalid_coords / total_rows * 100, 2) if total_rows > 0 else 0
            ),
        }

    # Check pickup < dropoff datetime
    if all(col in df.columns for col in ["pickup_datetime", "dropoff_datetime"]):
        invalid_times = df.filter(
            (col("dropoff_datetime").isNotNull())
            & (col("pickup_datetime") > col("dropoff_datetime"))
        ).count()
        issues["valid_timestamps"] = {
            "invalid_count": invalid_times,
            "invalid_percentage": (
                round(invalid_times / total_rows * 100, 2) if total_rows > 0 else 0
            ),
        }

    return issues


def check_uniqueness(df, key_column):
    """Check for duplicate keys"""
    if key_column not in df.columns:
        return {"status": "column_not_found", "duplicate_count": 0}

    total_rows = df.count()
    distinct_rows = df.select(key_column).distinct().count()
    duplicate_count = total_rows - distinct_rows

    return {
        "total_rows": total_rows,
        "distinct_rows": distinct_rows,
        "duplicate_count": duplicate_count,
        "duplicate_percentage": (
            round(duplicate_count / total_rows * 100, 2) if total_rows > 0 else 0
        ),
    }


def check_referential_integrity(df, foreign_key, reference_df, reference_key):
    """Check referential integrity"""
    if foreign_key not in df.columns or reference_key not in reference_df.columns:
        return {"status": "columns_not_found"}

    valid_keys = reference_df.select(reference_key).distinct()
    invalid_count = df.join(
        valid_keys, df[foreign_key] == valid_keys[reference_key], "left_anti"
    ).count()

    total_rows = df.count()

    return {
        "invalid_count": invalid_count,
        "invalid_percentage": (
            round(invalid_count / total_rows * 100, 2) if total_rows > 0 else 0
        ),
        "total_rows": total_rows,
    }


def calculate_quality_score(checks):
    """Calculate overall data quality score"""
    total_checks = 0
    passed_checks = 0

    # Schema check
    if "schema" in checks:
        total_checks += 1
        if checks["schema"]["passed"]:
            passed_checks += 1

    # Null checks
    if "nulls" in checks:
        for col_name, null_info in checks["nulls"].items():
            total_checks += 1
            if null_info["null_percentage"] < 5.0:  # Threshold: 5%
                passed_checks += 1

    # Business rules
    if "business_rules" in checks:
        for rule, rule_info in checks["business_rules"].items():
            total_checks += 1
            if rule_info["invalid_percentage"] < 5.0:  # Threshold: 5%
                passed_checks += 1

    # Uniqueness
    if "uniqueness" in checks:
        total_checks += 1
        if checks["uniqueness"]["duplicate_percentage"] < 1.0:  # Threshold: 1%
            passed_checks += 1

    # Referential integrity
    if "referential_integrity" in checks:
        for fk, fk_info in checks["referential_integrity"].items():
            total_checks += 1
            if fk_info.get("invalid_percentage", 100) < 1.0:  # Threshold: 1%
                passed_checks += 1

    quality_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    return round(quality_score, 2)


def validate_rides(spark, bronze_path):
    """Validate rides data"""
    print("Validating rides data...")

    # bronze_path should be like gs://bucket-name/bronze
    rides_df = spark.read.option("header", "true").csv(f"{bronze_path}/rides/*/*.csv")

    checks = {}

    # Schema validation
    required_columns = [
        "ride_id",
        "driver_id",
        "passenger_id",
        "pickup_datetime",
        "fare_amount",
        "pickup_latitude",
        "pickup_longitude",
    ]
    schema_passed, missing_columns = check_schema(rides_df, required_columns)
    checks["schema"] = {"passed": schema_passed, "missing_columns": missing_columns}

    # Null checks
    critical_columns = ["ride_id", "driver_id", "passenger_id", "fare_amount"]
    checks["nulls"] = check_nulls(rides_df, critical_columns)

    # Business rules
    checks["business_rules"] = check_business_rules_rides(rides_df)

    # Uniqueness
    checks["uniqueness"] = check_uniqueness(rides_df, "ride_id")

    return checks, rides_df.count()


def validate_drivers(spark, bronze_path):
    """Validate drivers data
    bronze_path should be like: gs://ride-analytics/bronze
    Drivers are in: bronze/drivers/drivers.csv
    """
    print("Validating drivers data...")

    drivers_df = spark.read.option("header", "true").csv(f"{bronze_path}/drivers/*.csv")

    checks = {}

    # Schema validation
    required_columns = ["driver_id", "name", "email", "registration_date"]
    schema_passed, missing_columns = check_schema(drivers_df, required_columns)
    checks["schema"] = {"passed": schema_passed, "missing_columns": missing_columns}

    # Null checks
    critical_columns = ["driver_id", "name", "email"]
    checks["nulls"] = check_nulls(drivers_df, critical_columns)

    # Uniqueness
    checks["uniqueness"] = check_uniqueness(drivers_df, "driver_id")

    return checks, drivers_df.count()


def validate_passengers(spark, bronze_path):
    """Validate passengers data
    bronze_path should be like: gs://ride-analytics/bronze
    Passengers are in: bronze/passengers/passengers.csv
    """
    print("Validating passengers data...")

    passengers_df = spark.read.option("header", "true").csv(
        f"{bronze_path}/passengers/*.csv"
    )

    checks = {}

    # Schema validation
    required_columns = ["passenger_id", "name", "email", "registration_date"]
    schema_passed, missing_columns = check_schema(passengers_df, required_columns)
    checks["schema"] = {"passed": schema_passed, "missing_columns": missing_columns}

    # Null checks
    critical_columns = ["passenger_id", "name", "email"]
    checks["nulls"] = check_nulls(passengers_df, critical_columns)

    # Uniqueness
    checks["uniqueness"] = check_uniqueness(passengers_df, "passenger_id")

    return checks, passengers_df.count()


def check_referential_integrity_all(
    spark, bronze_path, rides_df, drivers_df, passengers_df
):
    """Check referential integrity between tables"""
    print("Checking referential integrity...")

    checks = {}

    # Check driver_id in rides exists in drivers
    checks["rides_driver_id"] = check_referential_integrity(
        rides_df, "driver_id", drivers_df, "driver_id"
    )

    # Check passenger_id in rides exists in passengers
    checks["rides_passenger_id"] = check_referential_integrity(
        rides_df, "passenger_id", passengers_df, "passenger_id"
    )

    return checks


def main():
    """Main data quality check job"""
    if len(sys.argv) < 3:
        print("Usage: data_quality.py <bronze_path> <output_path>")
        sys.exit(1)

    bronze_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Starting data quality checks...")
    print(f"Bronze path: {bronze_path}")
    print(f"Output path: {output_path}")

    # Initialize Spark session
    spark = SparkSession.builder.appName("DataQualityChecks").getOrCreate()

    try:
        quality_report = {
            "timestamp": datetime.now().isoformat(),
            "bronze_path": bronze_path,
            "tables": {},
        }

        # Validate rides
        rides_checks, rides_count = validate_rides(spark, bronze_path)
        quality_report["tables"]["rides"] = {
            "record_count": rides_count,
            "checks": rides_checks,
        }

        # Validate drivers
        drivers_checks, drivers_count = validate_drivers(spark, bronze_path)
        quality_report["tables"]["drivers"] = {
            "record_count": drivers_count,
            "checks": drivers_checks,
        }

        # Validate passengers
        passengers_checks, passengers_count = validate_passengers(spark, bronze_path)
        quality_report["tables"]["passengers"] = {
            "record_count": passengers_count,
            "checks": passengers_checks,
        }

        # Check referential integrity
        rides_df = spark.read.option("header", "true").csv(
            f"{bronze_path}/rides/*/*.csv"
        )
        drivers_df = spark.read.option("header", "true").csv(
            f"{bronze_path}/drivers/*.csv"
        )
        passengers_df = spark.read.option("header", "true").csv(
            f"{bronze_path}/passengers/*.csv"
        )

        ref_integrity = check_referential_integrity_all(
            spark, bronze_path, rides_df, drivers_df, passengers_df
        )
        quality_report["tables"]["rides"]["checks"][
            "referential_integrity"
        ] = ref_integrity

        # Calculate quality scores
        for table_name, table_data in quality_report["tables"].items():
            quality_score = calculate_quality_score(table_data["checks"])
            quality_report["tables"][table_name]["quality_score"] = quality_score

        # Overall quality score
        overall_score = sum(
            table_data["quality_score"]
            for table_data in quality_report["tables"].values()
        ) / len(quality_report["tables"])
        quality_report["overall_quality_score"] = round(overall_score, 2)

        # Save quality report
        report_json = json.dumps(quality_report, indent=2)
        print("\n" + "=" * 50)
        print("DATA QUALITY REPORT")
        print("=" * 50)
        print(report_json)
        print("=" * 50)

        # Write report to GCS
        spark.sparkContext.parallelize([report_json]).saveAsTextFile(output_path)

        # Check if quality meets threshold
        quality_threshold = 95.0
        if overall_score >= quality_threshold:
            print(
                f"\n✅ Data quality check PASSED (Score: {overall_score}% >= {quality_threshold}%)"
            )
            sys.exit(0)
        else:
            print(
                f"\n❌ Data quality check FAILED (Score: {overall_score}% < {quality_threshold}%)"
            )
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error in data quality checks: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
