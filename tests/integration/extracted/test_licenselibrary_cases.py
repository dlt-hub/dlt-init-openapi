#
# Test different iterations of dotastats spec, this is FastAPI generated
#
from tests.integration.utils import get_dict_by_case


def test_simple_licenselibrary_load() -> None:
    source = get_dict_by_case("extracted", "licenselibrary_with_pagination.yml")
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "list",
        "table_name": "list",
        "endpoint": {
            "data_selector": "$",
            "path": "/licenselibrary/list",
        },
    }
