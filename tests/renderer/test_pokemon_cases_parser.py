#
# Test different iterations of pokemon
#
import os

from tests.renderer.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


def test_simple_poke_load() -> None:
    simple_poke = get_test_case_path("pokeapi_one_endpoint_no_paginator.yml")
    source = get_dict_from_open_api(simple_poke)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {"name": "pokemon_list", "endpoint": "/api/v2/pokemon/"}

    # source should also work
    source = get_source_from_open_api(simple_poke, base_url="https://pokeapi.co/")

    # this will actually hit the pokeapi
    source.resources["pokemon_list"].add_limit(15)
    assert len(list(source.resources["pokemon_list"])) == 300


def test_paged_poke_load() -> None:
    simple_poke = get_test_case_path("pokeapi_one_endpoint.yml")
    source = get_dict_from_open_api(simple_poke)
    assert len(source["resources"]) == 1

    # TODO: needs to have paginator later
    assert source["resources"][0] == {"name": "pokemon_list", "endpoint": "/api/v2/pokemon/"}

    # source should also work
    get_source_from_open_api(simple_poke)


def test_simple_child_table_poke_load() -> None:
    simple_poke = get_test_case_path("pokeapi_parent_child_fixed.yml")
    source = get_dict_from_open_api(simple_poke)
    assert len(source["resources"]) == 2
