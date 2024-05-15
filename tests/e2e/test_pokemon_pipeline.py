import duckdb

POKE_DUCKDB_FILE = "./pokemon-pipeline/pokemon_pipeline.duckdb"


def test_pokemon_pipeline() -> None:
    """Will only pass after creating and running pokemon test pipeline"""
    db = duckdb.connect(POKE_DUCKDB_FILE)

    # there should be 20 entries
    assert db.sql("SELECT count (*) from pokemon_data.pokemon").fetchone()[0] == 40

    # there should be 20 entries with pokemon details loaded
    # (the id is only loaded on the full request)
    assert db.sql("SELECT count (*) from pokemon_data.pokemon as p WHERE p.id IS NOT NULL").fetchone()[0] == 40
