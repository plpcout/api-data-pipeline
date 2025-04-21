import os
from calendar import monthrange
from datetime import datetime
from typing import Dict, Generator, List, Tuple, Union

import dlt
from dlt.destinations import filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define API constants
API_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
METHOD = "query"
BASE_URL = f"{API_URL}/{METHOD}"


@dlt.resource(name="earthquakes", write_disposition="replace")
def us_earthquakes(starttime: str, endtime: str) -> Generator[Dict, None, None]:
    """
    Resource function to fetch earthquake data from USGS API.
    
    Args:
        starttime: Start date in ISO format (YYYY-MM-DD)
        endtime: End date in ISO format (YYYY-MM-DD)
        
    Yields:
        Dictionary containing earthquake data
    """
    client = RESTClient(
        base_url=BASE_URL,
        paginator=OffsetPaginator(limit=20000, offset=1, total_path=None),
    )
    params = {
        "format": "geojson",
        "starttime": starttime,
        "endtime": endtime,
    }

    for page in client.paginate(BASE_URL, params=params):
        yield page


def create_pipeline() -> dlt.Pipeline:
    """
    Create and configure the DLT pipeline.
    
    Returns:
        Configured DLT pipeline
    """
    return dlt.pipeline(
        pipeline_name="api-to-gcs",
        # TODO: Disable enlighten in production
        progress="enlighten",
    )


def generate_date_ranges(years: List[str], months: List[int]) -> List[Tuple[str, str, str, str]]:
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
            last_day = monthrange(int(year), month)[1]
            endtime = f"{year}-{month_str}-{last_day}"
            
            date_ranges.append((year, month_str, starttime, endtime))
    
    return date_ranges


def build_destination_path(year: str, month: str) -> str:
    """
    Build the destination path for storing the data.
    
    Args:
        year: Year for which the data is being stored
        
    Returns:
        Full path to the destination
    """
    bucket_url = os.getenv("API_TO_GSC__DESTINATION__FILESYSTEM__BUCKET_URL")
    if not bucket_url:
        raise ValueError("API_TO_GSC__DESTINATION__FILESYSTEM__BUCKET_URL environment variable is not set")
        
    return os.path.join(
        bucket_url,
        "earthquakes_data",
        "raw",
        year,
        month
    )


def run_pipeline(
    years: List[str] = ["2015"],
    months: List[int] = list(range(1, 2))
) -> None:
    """
    Run the earthquake data pipeline for specified years and months.
    
    Args:
        years: List of years to process
        months: List of months to process
    """
    pipeline = create_pipeline()
    date_ranges = generate_date_ranges(years, months)
    
    for year, month_str, starttime, endtime in date_ranges:
        bucket_path = build_destination_path(year, month_str)
        
        print(f"Running pipeline for {year}/{month_str}")
        
        # load_info = pipeline.run(
        pipeline.run(
            us_earthquakes(
                starttime=starttime,
                endtime=endtime,
            ),
            destination=filesystem(bucket_path),
            dataset_name="files",
            loader_file_format="parquet",
        )
        
        # print(pipeline.last_trace)


if __name__ == "__main__":

    # Default run for 2015/01  
    # run_pipeline()

    # Parameters for the pipeline testing
    years = ["2023", "2024"]
    months = list(range(1, 13))
    run_pipeline(years, months)  

