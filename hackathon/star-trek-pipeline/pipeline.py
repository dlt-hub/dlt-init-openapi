import dlt

from star_trek import star_trek_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="star_trek_pipeline",
        destination='duckdb',
        dataset_name="star_trek_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = star_trek_source()
    info = pipeline.run(source)
    print(info)
