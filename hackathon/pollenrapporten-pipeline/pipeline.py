import dlt

from pollenrapporten import pollen_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="pollen_pipeline",
        destination='duckdb',
        dataset_name="pollen_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    info = pipeline.run(pollen_source())
    print(info)
