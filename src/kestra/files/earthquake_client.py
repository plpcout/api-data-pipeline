from typing import Dict, Generator

import dlt
from api_extract_schema import schema  # type: ignore
from config import BASE_URL
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import OffsetPaginator
from transformations import process_earthquake_record


@dlt.resource(
    name="earthquakes_api",
    write_disposition="replace",
    columns=schema,
)
def get_api_data_flat(starttime: str, endtime: str) -> Generator[Dict, None, None]:
    """Fetch earthquake records from the USGS API within [starttime, endtime).

    Paginates the API, applies per-record transformations (timestamp conversion,
    geometry flattening, reverse geocoding), and yields batches of processed
    records. Records missing geometry are dropped.
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

    for page in client.paginate(BASE_URL, params=params):
        processed = [process_earthquake_record(record) for record in page]
        yield [r for r in processed if r is not None]
