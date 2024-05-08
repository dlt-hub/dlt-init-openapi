#
# Test different iterations of museums spec
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_museums_load() -> None:
    source = get_dict_by_case("extracted", "quotesapi_simple_pagination.yml")

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
