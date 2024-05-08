#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_licenselibrary_load() -> None:
    source = get_dict_by_case("extracted", "licenselibrary_with_pagination.yml")
    assert len(source["resources"]) == 1

    # FIXME: they use skip and limit as offset and limit
    assert source["resources"][0] == {
        "name": "list",
        "endpoint": {
            "data_selector": "$",
            "path": "/licenselibrary/list",
            "paginator": {},
        },
    }
