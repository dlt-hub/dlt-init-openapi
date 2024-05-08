#
# Test different iterations of pollenrapporten spec, this is FastAPI generated
#
from tests.e2e.utils import get_dict_by_case


def test_simple_openartnft_load() -> None:
    source = get_dict_by_case("extracted", "pollenrapporten_with_pagination.yml")
    assert len(source["resources"]) == 1

    # FIXME: they use skip and limit as offset and limit
    assert source["resources"][0] == {
        "name": "PaginationLink",
        "endpoint": {
            "data_selector": "_links",
            "path": "/v1/pollen-types",
            "paginator": {
                "type": "offset",
                "initial_limit": "'100'",
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "_meta.totalRecords",
            },
        },
    }
