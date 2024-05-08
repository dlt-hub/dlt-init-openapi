#
# Test different iterations of museums spec
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_museums_load() -> None:
    source = get_dict_by_case("extracted", "museums_api_with_pagination.yml")
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


@pytest.mark.skip
def test_simple_museums_pagination() -> None:
    source = get_dict_by_case("extracted", "museums_api_events_with_pagination.yml")

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
