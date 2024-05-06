#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


# @pytest.mark.skip
def test_simple_openartnft_load() -> None:
    api_spec = get_test_case_path("licenselibrary_with_pagination.yml")
    source = get_dict_from_open_api(api_spec)
    assert len(source["resources"]) == 1

    # FIXME: they use skip and limit as offset and limit
    assert source["resources"][0] == {
        "name": "list_licenses_in_the_license_library_licenselibrary_list_get",
        "endpoint": {"data_selector": "$", "path": "/licenselibrary/list"},
    }

    # source should also work
    dltsource = get_source_from_open_api(api_spec, base_url="")
    dltsource.resources["list_licenses_in_the_license_library_licenselibrary_list_get"].add_limit(15)
