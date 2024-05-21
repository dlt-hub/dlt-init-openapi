import dlt

from hacker_news import hacker_news_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="hacker_news_pipeline",
        destination='duckdb',
        dataset_name="hacker_news_data",
        full_refresh=False,
        export_schema_path="schemas/export",
        progress="log"
    )
    source = hacker_news_source()
    # load transformer in parallel
    source.parallelize = True
    info = pipeline.run(source)
    print(info)
