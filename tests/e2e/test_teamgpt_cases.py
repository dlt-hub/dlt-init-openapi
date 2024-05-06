#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


# @pytest.mark.skip
def test_simple_openartnft_load() -> None:
    api_spec = get_test_case_path("teamgpt_with_pagination.yml")
    source = get_dict_from_open_api(api_spec)
    assert len(source["resources"]) == 1

    # FIXME: they use page and page_size parameters
    assert source["resources"][0] == {
        "name": "get_filesystem_objects_api_companies_uuid_filesystem_objects_get",
        "endpoint": {
            "data_selector": "$",
            "path": "/api/companies/{uuid}/filesystem_objects",
        },
    }

    # source should also work
    dltsource = get_source_from_open_api(api_spec, base_url="https://api-teamgpt.workhub.ai")
    dltsource.resources["get_filesystem_objects_api_companies_uuid_filesystem_objects_get"].add_limit(15)
