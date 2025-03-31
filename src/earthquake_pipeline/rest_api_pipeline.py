from typing import Any
from datetime import datetime

import dlt
from dlt.common.pendulum import pendulum
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator

# API Configuration
BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1"
QUERY_ENDPOINT = "query"

@dlt.resource(name="earthquakes", write_disposition="append")
def usgs_earthquake_source(
    start_time: datetime | pendulum.DateTime | None = None,
    end_time: datetime | pendulum.DateTime | None = None,
    min_magnitude: float = 0.0,
) -> Any:
    """Create a REST API source for the USGS Earthquake API with improved pagination."""
    # Set default time range if not provided
    end_time = end_time or pendulum.now()
    start_time = start_time or end_time.subtract(hours=1)

    # Initialize REST client with better pagination support
    client = RESTClient(
        base_url=BASE_URL,
        paginator=OffsetPaginator(
            limit=20000,
            offset=1,
            total_path=None
        )
    )

    params = {
        "format": "geojson",
        "starttime": start_time.isoformat(),
        "endtime": end_time.isoformat(),
        "minmagnitude": min_magnitude,
        "orderby": "time",
    }
    
    for page in client.paginate(f"{BASE_URL}/{QUERY_ENDPOINT}", params=params):
        yield page


def load_earthquakes() -> None:
    """Run the earthquake data pipeline with improved configuration."""
    pipeline = dlt.pipeline(
        pipeline_name="usgs_earthquakes",
        destination='filesystem',
        dataset_name="earthquake_data",
        progress="enlighten",  # Better progress visualization
    )

    # Create source with configuration for last 6 hours
    source = usgs_earthquake_source(
        start_time=pendulum.now().subtract(hours=6),
        min_magnitude=1.0,
    )

    # Run the pipeline with parquet format for better performance
    load_info = pipeline.run(
        source,
        loader_file_format="parquet",  # Use parquet for better performance
    )
    
    print(f"Pipeline completed. Load info: {load_info}")
    print(f"Last trace: {pipeline.last_trace}")


if __name__ == "__main__":
    load_earthquakes()
