import os
from calendar import monthrange
from typing import Dict, Generator, List, Tuple

import dlt
import pendulum
from dlt.destinations import bigquery, filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from dotenv import load_dotenv

load_dotenv()

# API constants
API_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
METHOD = "query"
BASE_URL = f"{API_URL}/{METHOD}"


def _process_earthquake_record(record: Dict) -> Dict:
    """
    Process and transform earthquake record by converting timestamps and flattening geometry.

    Args:
        record: Dictionary containing earthquake record data

    Returns:
        Processed record with transformed timestamps and flattened geometry
    """
    time = record["properties"]["time"]
    record["properties"]["time"] = pendulum.from_timestamp(
        time / 1000, tz="UTC"
    ).replace(microsecond=0).to_iso8601_string()
    updated = record["properties"]["updated"]
    record["properties"]["updated"] = pendulum.from_timestamp(
        updated / 1000, tz="UTC"
    ).start_of(unit="second").to_iso8601_string()

    if "geometry" not in record:
        return None
    record["properties"]["g_type"] = record["geometry"]["type"]
    coordinates = record["geometry"]["coordinates"]
    record["properties"]["g_longitude"] = coordinates[0]
    record["properties"]["g_latitude"] = coordinates[1]
    record["properties"]["g_depth"] = coordinates[2]
    del record["geometry"]
    return record

def _generate_date_ranges(
    years: List[int], months: List[int]
) -> List[Tuple[str, str, str, str]]:
    """
    Generate start and end dates for each month in the given years.

    Args:
        years: List of years as strings (e.g., ["2021", "2022"])
        months: List of month numbers (e.g., range(1, 13))

    Returns:
        List of tuples containing (year, month_str, starttime, endtime)
    """
    date_ranges = []
    for year in years:
        for month in months:
            # Format month to be two digits
            month_str = f"{month:02}"
            starttime = f"{year}-{month_str}-01"
            # Get the last day of the current month
            last_day = monthrange(year, month)[1]
            endtime = f"{year}-{month_str}-{last_day}"

            date_ranges.append((year, month_str, starttime, endtime))

    return date_ranges

@dlt.resource(
    name="earthquakes_api",
    write_disposition="replace",
)
def get_api_data_flat(
    starttime: str,
    endtime: str,
) -> Generator[Dict, None, None]:
    """
    Resource function to fetch earthquake data from USGS API with flattened coordinates.
    Extracts longitude, latitude, and depth from geometry.coordinates.

    Args:
        starttime: Start date in ISO format (YYYY-MM-DD)
        endtime: End date in ISO format (YYYY-MM-DD)

    Yields:
        Dictionary containing earthquake data with flattened coordinates
    """
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
            yield record


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
        raise ValueError(
            "DESTINATION__FILESYSTEM__BUCKET_URL environment variable is not set"
        )

    # return os.path.join(bucket_url, "earthquakes_data", "raw", year, month)
    return os.path.join(bucket_url, "earthquakes_data", "raw")


def run_pipeline(years: List[int] = [2024], months: List[int] = list(range(1, 13)))  -> None:
    """
    Run the earthquake data pipeline for specified years and months.

    Args:
        years: List of years to process
        months: List of months to process
    """
    pipeline = create_pipeline()
    date_ranges = _generate_date_ranges(years, months)

    for year, month_str, starttime, endtime in date_ranges:
        bucket_path = build_destination_bucket_path(year, month_str)

        print(f"Running pipeline for {year}/{month_str}")

        load_info = pipeline.run(
            get_api_data_flat(
                starttime=starttime,
                endtime=endtime,
            ),
            dataset_name="files",
            table_name=f"raw_eq_data_{year}_{month_str}",
            loader_file_format="parquet",
            destination=bigquery(
                dataset_name="raw_eq_dataset",
            ),
            staging=filesystem(
                bucket_path,
                extra_placeholders={
                    "file_name": f"extract_{year}_{month_str}",
                },
                layout="{table_name}/{file_name}.{ext}",
            ),
        )
        print(load_info)


if __name__ == "__main__":
    years = [2024]
    months = list(range(1, 13))
    run_pipeline(years, months)
