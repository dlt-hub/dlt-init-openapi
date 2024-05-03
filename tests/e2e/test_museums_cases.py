#
# Test different iterations of pokemon
#
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


def test_simple_museums_load() -> None:
    museums_spec = get_test_case_path("museums_api_with_pagination.yml")
    source = get_dict_from_open_api(museums_spec)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "get_museum_hours",
        "endpoint": {"path": "/museum-hours", "data_selector": "$"},
        # FIXME: This doesn't parse referenced query parameters for pagination
        "paginator": {
            "limit_param": "limit",
            "offset_param": "page",
            "type": "offset",
        },
    }

    # source should also work
    dltsource = get_source_from_open_api(museums_spec, base_url="https://api.fake-museum-example.com/v1")
    dltsource.resources["get_museum_hours"].add_limit(15)
