import dlt
from dlt.sources.filesystem import filesystem, read_parquet
from dotenv import load_dotenv

load_dotenv()



filesystem_resource = filesystem(
  # ... ENV variables are providing the values
)

filesystem_pipe = filesystem_resource | read_parquet()
# filesystem_pipe.apply_hints(incremental=dlt.sources.incremental("properties__time"))


pipeline = dlt.pipeline(
    pipeline_name="testing_pipe",
    destination="bigquery",
)

# load_info = pipeline.run(filesystem_pipe.with_name("table_name"))
load_info = pipeline.run(
    filesystem_pipe,
    table_name="my_testing_table",
    write_disposition="append",
)
print(load_info)
print(pipeline.last_trace.last_normalize_info)
