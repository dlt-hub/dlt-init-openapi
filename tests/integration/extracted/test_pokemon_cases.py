#
# Test different iterations of pokemon
#
from tests.integration.utils import get_dict_by_case


def test_simple_poke_load() -> None:
    source = get_dict_by_case("extracted", "pokeapi_one_endpoint_no_paginator.yml")
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "pokemon",
        "table_name": "pokemon",
        "endpoint": {"path": "/api/v2/pokemon/", "paginator": "auto"},
    }


def test_paged_poke_load() -> None:
    source = get_dict_by_case("extracted", "pokeapi_one_endpoint.yml")
    assert len(source["resources"]) == 1

    assert source["client"]["paginator"] == {
        "limit": 20,
        "limit_param": "limit",
        "offset_param": "offset",
        "type": "offset",
        "total_path": "count",
    }

    assert source["resources"][0] == {
        "name": "pokemon",
        "table_name": "pokemon",
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "path": "/api/v2/pokemon/",
            "data_selector": "results",
            "path": "/api/v2/pokemon/",
        },
    }


def test_simple_child_table_poke_load() -> None:
    source = get_dict_by_case("extracted", "pokeapi_parent_child_fixed.yml")

    assert len(source["resources"]) == 2

    assert source["client"]["paginator"] == {
        "limit": 20,
        "limit_param": "limit",
        "offset_param": "offset",
        "type": "offset",
        "total_path": "count",
    }

    # root resource
    assert source["resources"][0] == {
        "name": "pokemon_list",
        "table_name": "pokemon",
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "path": "/api/v2/pokemon/",
            "data_selector": "results",
        },
    }

    # resolve transformer
    assert source["resources"][1] == {
        "name": "pokemon_read",
        "table_name": "pokemon",
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            # "paginator": "auto",
            "path": "/api/v2/pokemon/{name}/",
            "data_selector": "$",
            "params": {
                "name": {
                    "type": "resolve",
                    "resource": "pokemon_list",
                    "field": "name",
                },
            },
        },
    }
