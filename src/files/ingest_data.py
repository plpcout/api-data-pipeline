import argparse
import os
from calendar import monthrange
from typing import Dict, Generator, Tuple

import dlt
import pendulum
import reverse_geocode as rg
from api_extract_schema import schema  # type: ignore
from dlt.destinations import bigquery, filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from kestra import Kestra

# API constants
API_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
METHOD = "query"
BASE_URL = f"{API_URL}/{METHOD}"

logger = Kestra.logger()


def _get_location_details(latitude: float, longitude: float) -> Dict[str, str]:
    """
    Get location details from coordinates using reverse geocoding.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Dictionary containing location details (country_code, country, city, population, state)
    """
    cords = (latitude, longitude)
    geo_details = rg.get(cords)
    results = {
        "country_code": geo_details.get("country_code", None),
        "country": geo_details.get("country", None),
        "city": geo_details.get("city", None),
        "population": geo_details.get("population", None),
        "state": geo_details.get("state", None),
    }

    return results


def _convert_timestamp_to_iso(timestamp: int) -> str:
    """
    Convert millisecond timestamp to ISO 8601 string.

    Args:
        timestamp: Unix timestamp in milliseconds

    Returns:
        ISO 8601 formatted string
    """
    return (
        pendulum.from_timestamp(timestamp / 1000, tz="UTC")
        .replace(microsecond=0)
        .to_iso8601_string()
    )


def _process_earthquake_record(record: Dict) -> Dict:
    """
    Process and transform earthquake record by converting timestamps and flattening geometry.

    Args:
        record: Dictionary containing earthquake record data

    Returns:
        Processed record with transformed timestamps and flattened geometry
    """

    # Convert timestamps
    record["properties"]["time"] = _convert_timestamp_to_iso(record["properties"]["time"])
    record["properties"]["updated"] = _convert_timestamp_to_iso(record["properties"]["updated"])

    # Flatten geometry
    if "geometry" not in record:
        return None
    record["properties"]["g_type"] = record["geometry"]["type"]
    coordinates = record["geometry"]["coordinates"]
    longitude = coordinates[0]
    latitude = coordinates[1]
    depth = coordinates[2]
    record["properties"]["g_longitude"] = longitude
    record["properties"]["g_latitude"] = latitude
    record["properties"]["g_depth"] = depth

    # Reverse geocode to get location information
    geo_details = _get_location_details(latitude, longitude)
    record["properties"]["country_code"] = geo_details["country_code"]
    record["properties"]["country"] = geo_details["country"]
    record["properties"]["state"] = geo_details["state"]
    record["properties"]["city"] = geo_details["city"]
    record["properties"]["population"] = geo_details["population"]

    del record["geometry"]
    return record


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
            for record in page:
                record = _process_earthquake_record(record)
            yield page
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

    logger.info(f"Running pipeline for {year}/{month}")

    load_info = pipeline.run(
        get_api_data_flat(
            starttime=starttime,
            endtime=endtime,
        ),
        dataset_name="files",
        table_name=f"raw_eq_data_{year}_{month}",
        loader_file_format="parquet",
        destination=bigquery(
            dataset_name="raw_eq_dataset",
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
