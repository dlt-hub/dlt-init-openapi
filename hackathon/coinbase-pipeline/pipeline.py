import dlt

from coinbase import coinbase_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="coinbase_pipeline",
        destination='duckdb',
        dataset_name="coinbase_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = coinbase_source()
    info = pipeline.run(source)
    print(info)
