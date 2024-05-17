#
# Test different iterations of dotastats spec, this is FastAPI generated
#
from tests.integration.utils import get_dict_by_case


def test_simple_openartnft_load() -> None:
    source = get_dict_by_case("extracted", "openartnft_with_pagination.yml")
    assert len(source["resources"]) == 2

    assert source["client"]["paginator"] == {
        "limit": 10,
        "limit_param": "limit",
        "maximum_offset": 20,
        "offset_param": "skip",
        "type": "offset",
        "total_path": "",
    }

    assert source["resources"][0] == {
        "name": "gallery",
        "table_name": "gallery",
        "endpoint": {
            "params": {},
            "data_selector": "$",
            "path": "/galleries/",
        },
    }
    assert source["resources"][1] == {
        "name": "item",
        "table_name": "item",
        "endpoint": {
            "params": {},
            "data_selector": "$",
            "path": "/items/",
        },
    }
