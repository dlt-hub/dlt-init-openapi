#
# Test different iterations of museums spec
#
import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.mark.skip
def test_simple_museums_load() -> None:
    api_spec = get_test_case_path("quotesapi_simple_pagination.yml")
    source = get_dict_from_open_api(api_spec)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "get_quotelist",
        "endpoint": {"data_selector": "$", "path": "/quote/list"},
        # FIXME: This doesn't parse referenced query parameters for pagination
        "paginator": {
            "limit_param": "limit",
            "offset_param": "start",
            "type": "offset",
        },
    }

    # source should also work
    dltsource = get_source_from_open_api(api_spec, base_url="https://quotes.rest")
    dltsource.resources["get_quotelist"].add_limit(15)
