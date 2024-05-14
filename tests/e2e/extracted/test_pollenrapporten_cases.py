#
# Test different iterations of pollenrapporten spec, this is FastAPI generated
#
from tests.e2e.utils import get_dict_by_case


def test_simple_openartnft_load() -> None:
    source = get_dict_by_case("extracted", "pollenrapporten_with_pagination.yml")
    assert len(source["resources"]) == 1
    assert source["resources"][0] == {
        "name": "pagination_link",
        "table_name": "pagination_link",
        "endpoint": {
            "data_selector": "_links",
            "path": "/v1/pollen-types",
            "paginator": {
                "type": "offset",
                "limit": 100,
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "_meta.totalRecords",
            },
        },
    }
