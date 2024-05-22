import dlt

from chicago import chicago_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="chicago_pipeline",
        destination='duckdb',
        dataset_name="chicago_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = chicago_source()
    source.add_limit(50)
    info = pipeline.run(source)
    print(info)
