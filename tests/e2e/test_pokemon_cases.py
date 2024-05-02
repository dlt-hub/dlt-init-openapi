#
# Test different iterations of pokemon
#
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


def test_simple_poke_load() -> None:
    simple_poke = get_test_case_path("pokeapi_one_endpoint_no_paginator.yml")
    source = get_dict_from_open_api(simple_poke)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "pokemon_list",
        "endpoint": {"path": "/api/v2/pokemon/", "data_selector": "$"},
    }

    # source should also work
    dltsource = get_source_from_open_api(simple_poke, base_url="https://pokeapi.co/")

    # this will actually hit the pokeapi
    dltsource.resources["pokemon_list"].add_limit(15)
    # assert len(list(dltsource.resources["pokemon_list"])) == 300


def test_paged_poke_load() -> None:
    simple_poke = get_test_case_path("pokeapi_one_endpoint.yml")
    source = get_dict_from_open_api(simple_poke)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "pokemon_list",
        "endpoint": {
            "path": "/api/v2/pokemon/",
            "data_selector": "results",
            "paginator": {
                "initial_limit": 20,
                "limit_param": "limit",
                "offset_param": "offset",
                "type": "offset",
                "total_path": "count",
            },
            "path": "/api/v2/pokemon/",
        },
    }

    # source should also work
    get_source_from_open_api(simple_poke)


def test_simple_child_table_poke_load() -> None:
    simple_poke = get_test_case_path("pokeapi_parent_child_fixed.yml")
    source = get_dict_from_open_api(simple_poke)
    assert len(source["resources"]) == 2

    # root resource
    assert source["resources"][0] == {
        "name": "pokemon_list",
        "endpoint": {
            "path": "/api/v2/pokemon/",
            "data_selector": "results",
            "paginator": {
                "initial_limit": 20,
                "limit_param": "limit",
                "offset_param": "offset",
                "type": "offset",
                "total_path": "count",
            },
        },
    }

    # resolve transformer
    assert source["resources"][1] == {
        "name": "pokemon_read",
        "endpoint": {
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

    # building the source should also work
    get_source_from_open_api(simple_poke)
