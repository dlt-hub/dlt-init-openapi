#
# Test different iterations of museums spec
#
import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.mark.skip
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


@pytest.mark.skip
def test_simple_museums_pagination() -> None:
    museums_spec = get_test_case_path("museums_api_events_with_pagination.yml")
    source = get_dict_from_open_api(museums_spec)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "list_special_events",
        "endpoint": {"path": "/special-events", "data_selector": "$"},
        # FIXME: This doesn't parse referenced query parameters for pagination
        "paginator": {
            "limit_param": "limit",
            "offset_param": "page",
            "type": "offset",
        },
    }

    # source should also work
    dltsource = get_source_from_open_api(museums_spec, base_url="https://api.fake-museum-example.com/v1")
    dltsource.resources["list_special_events"].add_limit(15)
