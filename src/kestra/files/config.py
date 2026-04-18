import os

# USGS Earthquake API endpoints
API_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
METHOD = "query"
BASE_URL = f"{API_URL}/{METHOD}"


def build_destination_bucket_path() -> str:
    """Return the GCS path where raw earthquake parquet files should land."""
    bucket_url = os.getenv("DESTINATION__FILESYSTEM__BUCKET_URL")
    if not bucket_url:
        raise ValueError("DESTINATION__FILESYSTEM__BUCKET_URL environment variable is not set")
    return os.path.join(bucket_url, "earthquakes_data", "raw")


def build_destination_bq_dataset() -> str:
    """Return the BigQuery dataset name where processed data is loaded."""
    dataset_name = os.getenv("DESTINATION__BIGQUERY__DATASET_NAME")
    if not dataset_name:
        raise ValueError("DESTINATION__BIGQUERY__DATASET_NAME environment variable is not set")
    return dataset_name
