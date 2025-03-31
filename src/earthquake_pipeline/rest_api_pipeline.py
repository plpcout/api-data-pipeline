import os
from calendar import monthrange

import dlt
from dlt.destinations import filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from dotenv import load_dotenv

load_dotenv()

# Define the base URL of the API, ENDPOINT, and STARTING_PAGE
API_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
METHOD = "query"
BASE_URL = f"{API_URL}/{METHOD}"

# Testing parameters for the pipeline
years = ["2021","2022", "2023", "2024"]  # Example years
months = range(1, 13)  # Months from 1 to 12


@dlt.resource(name="earthquakes", write_disposition="replace")
def us_earthquakes(starttime, endtime):
    client = RESTClient(
        base_url=BASE_URL,
        paginator=OffsetPaginator(limit=20000, offset=1, total_path=None),
    )
    params = {
        "format": "geojson",
        "starttime": starttime,
        "endtime": endtime,
    }

    for page in client.paginate(
        BASE_URL, params=params
    ):  # <--- API endpoint for retrieving taxi ride data
        yield page


pipeline = dlt.pipeline(
    pipeline_name="us_earthquakes",
    progress="enlighten",  # <--- Install enlighten for better visualization. Otherwise comment this line
)


for year in years:
    for month in months:
        # Format month to be two digits
        month_str = f"{month:02}"
        starttime = f"{year}-{month_str}-01"
        last_day = monthrange(int(year), month)[
            1
        ]  # Get the last day of the current month
        endtime = f"{year}-{month_str}-{last_day}"

        bucket_path = os.path.join(
            os.getenv("DESTINATION__FILESYSTEM__BUCKET_URL"),  # e.g. s3://my-bucket
            "earthquakes_data",  # e.g. earthquakes_data
            "raw",  # Subdirectory for raw data
            year
        )


        print(f"Running pipeline for {year}/{month_str}")
        load_info = pipeline.run(
            us_earthquakes(
                starttime=starttime,
                endtime=endtime,
            ),
            destination=filesystem(bucket_path),
            dataset_name=month_str,
            loader_file_format="parquet",
        )

        print(pipeline.last_trace)
