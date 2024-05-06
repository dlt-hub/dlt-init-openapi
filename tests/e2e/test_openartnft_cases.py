#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


@pytest.mark.skip
def test_simple_openartnft_load() -> None:
    api_spec = get_test_case_path("openartnft_with_pagination.yml")
    source = get_dict_from_open_api(api_spec)
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

    # source should also work
    dltsource = get_source_from_open_api(api_spec, base_url="")
    dltsource.resources["read_item_filtered_items_get"].add_limit(15)
    dltsource.resources["read_galleries_public_data_galleries_get"].add_limit(15)
