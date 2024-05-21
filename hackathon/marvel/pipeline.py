import dlt

from marvel import marvel_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="marvel_pipeline",
        destination="duckdb",
        dataset_name="marvel_data",
        full_refresh=False,
        export_schema_path="schemas/export",
    )
    source = marvel_source()
    info = pipeline.run(source)
    print(info)
