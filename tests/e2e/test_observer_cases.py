#
# Test different iterations of observer spec: FastAPI generated
#
import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.mark.skip
def test_simple_observer_load() -> None:
    api_spec = get_test_case_path("observer_with_pagination.yml")
    source = get_dict_from_open_api(api_spec)
    assert len(source["resources"]) == 2

    assert source["resources"][1] == {
        # FIXME: generates wierd resource name
        "name": "admin_get_users_admin_users_get",
        "endpoint": {
            "data_selector": "items",
            "path": "/admin/users",
            "paginator": {
                "type": "offset",
                "initial_limit": "'100'",
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "total",
            },
        },
    }
    assert source["resources"][0] == {
        # FIXME: generates wierd resource name
        "name": "get_offices_offices_get",
        "endpoint": {
            "data_selector": "items",
            "path": "/offices",
            "paginator": {
                "type": "offset",
                "initial_limit": "'100'",
                "offset_param": "offset",
                "limit_param": "limit",
                "total_path": "total",
            },
        },
    }

    # source should also work
    dltsource = get_source_from_open_api(api_spec, base_url="https://api.opendota.com/api")
    dltsource.resources["admin_get_users_admin_users_get"].add_limit(15)
