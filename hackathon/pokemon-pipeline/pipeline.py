import dlt

from pokemon import pokemon_source


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="pokemon_pipeline",
        destination='duckdb',
        dataset_name="pokemon_data",
        full_refresh=False,
        export_schema_path="schemas/export"
    )
    source = pokemon_source()
    info = pipeline.run(source)
    print(info)
