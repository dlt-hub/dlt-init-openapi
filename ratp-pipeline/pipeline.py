import dlt

from ratp import ratp_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="ratp_pipeline",
        destination='duckdb',
        dataset_name="ratp_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = ratp_source()
    info = pipeline.run(source)
    print(info)
