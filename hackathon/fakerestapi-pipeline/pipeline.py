import dlt

from fakerestapi import fakerestapi_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="fakerestapi_pipeline",
        destination="duckdb",
        dataset_name="fakerestapi_data",
        full_refresh=False,
        export_schema_path="schemas/export",
    )
    source = fakerestapi_source()
    info = pipeline.run(source)
    print(info)
