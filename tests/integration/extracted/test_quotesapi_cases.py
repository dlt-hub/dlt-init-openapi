#
# Test different iterations of museums spec
#

from tests.integration.utils import get_dict_by_case


def test_simple_quotesapi_load() -> None:
    source = get_dict_by_case("extracted", "quotesapi_simple_pagination.yml")

    assert len(source["resources"]) == 1

    assert source["client"]["paginator"] == {
        "limit": 10,
        "limit_param": "limit",
        "maximum_offset": 20,
        "offset_param": "start",
        "type": "offset",
        "total_path": "",
    }

    assert source["resources"][0] == {
        "name": "list",
        "table_name": "list",
        "endpoint": {
            "data_selector": "$",
            "path": "/quote/list",
        },
    }
