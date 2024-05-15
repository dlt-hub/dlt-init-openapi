#
# Test different iterations of museums spec
#
from tests.e2e.utils import get_dict_by_case


def test_simple_museums_load() -> None:
    source = get_dict_by_case("extracted", "museums_api_with_pagination.yml")
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "museum_daily_hours",
        "table_name": "museum_daily_hours",
        "endpoint": {
            "path": "/museum-hours",
            "data_selector": "$",
            "paginator": {
                "maximum_page": 20,
                "page_param": "page",
                "type": "page_number",
            },
        },
    }


def test_simple_museums_pagination() -> None:
    source = get_dict_by_case("extracted", "museums_api_events_with_pagination.yml")

    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "special_event_response",
        "table_name": "special_event_response",
        "endpoint": {
            "path": "/special-events",
            "data_selector": "$",
            "paginator": {
                "maximum_page": 20,
                "page_param": "page",
                "type": "page_number",
            },
        },
        "primary_key": "eventId",
        "write_disposition": "merge",
    }
