import argparse
from calendar import monthrange
from typing import Tuple

import dlt
from config import build_destination_bq_dataset, build_destination_bucket_path
from dlt.destinations import bigquery, filesystem
from earthquake_client import get_api_data_flat

from kestra import Kestra

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


def create_pipeline() -> dlt.Pipeline:
    """
    Create and configure the DLT pipeline.

    Returns:
        Configured DLT pipeline
    """
    return dlt.pipeline(pipeline_name="api_extract")


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
