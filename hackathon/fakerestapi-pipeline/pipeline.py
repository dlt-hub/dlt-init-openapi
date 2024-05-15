import dlt

from fakeapi import fakeapi_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="fakeapi_pipeline",
        destination='duckdb',
        dataset_name="fakeapi_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    info = pipeline.run(fakeapi_source())
    print(info)
