import dlt

from pollenrapporten import pollenrapporten_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="pollenrapporten_pipeline",
        destination="duckdb",
        dataset_name="pollenrapporten_data",
        full_refresh=False,
        export_schema_path="schemas/export",
    )
    source = pollenrapporten_source()
    info = pipeline.run(source)
    print(info)
