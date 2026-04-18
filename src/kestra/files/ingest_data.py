import argparse
import os
from calendar import monthrange
from typing import Dict, Generator, Tuple

import dlt
from api_extract_schema import schema  # type: ignore
from dlt.destinations import bigquery, filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from transformations import process_earthquake_record

from kestra import Kestra

# API constants
API_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
METHOD = "query"
BASE_URL = f"{API_URL}/{METHOD}"

logger = Kestra.logger()


def _generate_date_ranges(year, month) -> Tuple[str, str]:
    """
    Generate start and end dates for each month in the given years.

    Args:
        year: Years as string (e.g., "2021")
        month: Month number as string (e.g., "01")

    Returns:
        Tuple containing (starttime, endtime)
    """
    starttime = f"{year}-{month}-01"
    last_day = monthrange(int(year), int(month))[1]
    endtime = f"{year}-{month}-{last_day}"

    return (starttime, endtime)


@dlt.resource(
    name="earthquakes_api",
    write_disposition="replace",
    columns=schema,
)
def get_api_data_flat(starttime: str, endtime: str) -> Generator[Dict, None, None]:
    """
    Resource function to fetch earthquake data from USGS API with flattened coordinates.
    Extracts longitude, latitude, and depth from geometry.coordinates.

    Args:
        starttime: Start date in ISO format (YYYY-MM-DD)
        endtime: End date in ISO format (YYYY-MM-DD)

    Yields:
        Dictionary containing earthquake data with flattened coordinates
    """
    try:
        client = RESTClient(
            base_url=BASE_URL,
            paginator=OffsetPaginator(limit=20000, offset=1, total_path=None),
            data_selector="features",
        )
        params = {
            "format": "geojson",
            "starttime": starttime,
            "endtime": endtime,
        }

        for page in client.paginate(
            BASE_URL,
            params=params,
        ):
            processed = [process_earthquake_record(record) for record in page]
            yield [r for r in processed if r is not None]
    except Exception as e:
        logger.info(f"Error fetching earthquake data: {e}")
        raise


def create_pipeline() -> dlt.Pipeline:
    """
    Create and configure the DLT pipeline.

    Returns:
        Configured DLT pipeline
    """
    return dlt.pipeline(pipeline_name="api_extract")


def build_destination_bucket_path() -> str:
    """
    Build the destination path for storing the data.

    Args:
        year: Year for which the data is being stored

    Returns:
        Full path to the destination
    """
    bucket_url = os.getenv("DESTINATION__FILESYSTEM__BUCKET_URL")
    if not bucket_url:
        raise ValueError("DESTINATION__FILESYSTEM__BUCKET_URL environment variable is not set")

    # return os.path.join(bucket_url, "earthquakes_data", "raw", year, month)
    return os.path.join(bucket_url, "earthquakes_data", "raw")


def build_destination_bq_dataset() -> str:
    """
    Build the destination path for storing the data.

    Args:
        year: Year for which the data is being stored

    Returns:
        Full path to the destination
    """
    dataset_name = os.getenv("DESTINATION__BIGQUERY__DATASET_NAME")
    if not dataset_name:
        raise ValueError("DESTINATION__BIGQUERY__DATASET_NAME environment variable is not set")

    return dataset_name


def run_pipeline(year, month) -> None:
    """
    Run the earthquake data pipeline for a specific year and month.

    Args:
        year: Year to process (string)
        month: Month to process (string)
    """

    pipeline = create_pipeline()
    starttime, endtime = _generate_date_ranges(year, month)

    bucket_path = build_destination_bucket_path()
    bq_dataset_name = build_destination_bq_dataset()

    logger.info(f"Running pipeline for {year}/{month}")
    logger.info(f"DataLake - Staging data into GCS Bucket: {bucket_path}")
    logger.info(f"DataWarehousing - Loading data into BigQuery Dataset: {bq_dataset_name}")

    load_info = pipeline.run(
        get_api_data_flat(
            starttime=starttime,
            endtime=endtime,
        ),
        dataset_name="files",
        table_name=f"raw_eq_data_{year}_{month}",
        loader_file_format="parquet",
        destination=bigquery(
            dataset_name=bq_dataset_name,
        ),
        staging=filesystem(
            bucket_path,
            extra_placeholders={
                "file_name": f"extract_{year}_{month}",
            },
            layout="{table_name}/{file_name}.{ext}",
        ),
    )
    logger.info(load_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process earthquake data for a specific year and month"
    )
    parser.add_argument("year", type=str, nargs="?")
    parser.add_argument("month", type=str, nargs="?")

    args = parser.parse_args()

    run_pipeline(args.year, args.month)
