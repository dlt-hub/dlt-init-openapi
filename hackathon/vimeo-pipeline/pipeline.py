import dlt

from vimeo import vimeo_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="vimeo_pipeline",
        destination='duckdb',
        dataset_name="vimeo_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = vimeo_source()
    info = pipeline.run(source)
    print(info)
