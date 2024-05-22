import dlt

from google_bigquery import google_bigquery_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="google_bigquery_pipeline",
        destination='duckdb',
        dataset_name="google_bigquery_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = google_bigquery_source()
    info = pipeline.run(source)
    print(info)
