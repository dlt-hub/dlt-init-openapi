import dlt

from game_of_thrones import game_of_thrones_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="game_of_thrones_pipeline",
        destination='duckdb',
        dataset_name="game_of_thrones_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = game_of_thrones_source()
    info = pipeline.run(source)
    print(info)
