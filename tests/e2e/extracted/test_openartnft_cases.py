#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_openartnft_load() -> None:
    source = get_dict_by_case("extracted", "openartnft_with_pagination.yml")
    assert len(source["resources"]) == 2

    # FIXME: they use skip and limit as offset and limit
    assert source["resources"][0] == {
        "name": "read_item_filtered_items_get",
        "endpoint": {"data_selector": "$", "path": "/items/"},
    }
    assert source["resources"][1] == {
        "name": "read_galleries_public_data_galleries_get",
        "endpoint": {"data_selector": "$", "path": "/galleries/"},
    }
