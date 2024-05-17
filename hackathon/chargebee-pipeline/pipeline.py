import dlt

from chargebee import chargebee_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="chargebee_pipeline",
        destination='duckdb',
        dataset_name="chargebee_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = chargebee_source()
    info = pipeline.run(source)
    print(info)
