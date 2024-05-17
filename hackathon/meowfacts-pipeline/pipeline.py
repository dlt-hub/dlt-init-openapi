import dlt

from meowfacts import meowfacts_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="meowfacts_pipeline",
        destination='duckdb',
        dataset_name="meowfacts_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = meowfacts_source()
    info = pipeline.run(source)
    print(info)
