#
# Test different iterations of dotastats spec
#
import pytest

from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_test_case_path


@pytest.mark.skip
def test_simple_zoom_load() -> None:
    api_spec = get_test_case_path("zoom_with_pagination.yml")
    source = get_dict_from_open_api(api_spec)
    assert len(source["resources"]) == 2

    # FIXME: this spec defines schema right in the endpoints
    # pydantic.error_wrappers.ValidationError: 2 validation errors for OpenAPI
    # paths -> /contacts -> get -> responses -> 200 -> description
    #   field required (type=value_error.missing)
    # paths -> /contacts -> get -> responses -> 200 -> $ref
    #   field required (type=value_error.missing)
    assert source["resources"][0] == {
        "name": "get_accounts",
        "endpoint": {"path": "/accounts", "data_selector": "$"},
        # FIXME: No paginator resolved
        # parameters:
        # - name: next_page_token
        #   in: query
        #   required: false
        #   schema:
        #     type: string
        "paginator": {},
    }

    dltsource = get_source_from_open_api(api_spec, base_url="https://api.zoom.us/v2")
    assert source["resources"][0] == {
        "name": "get_contacts",
        "endpoint": {"path": "/contacts", "data_selector": "$"},
        # FIXME: No paginator resolved
        # parameters:
        # - name: next_page_token
        #   in: query
        #   required: false
        #   schema:
        #     type: string
        "paginator": {},
    }

    # source should also work
    dltsource.resources["get_accounts"].add_limit(15)
    dltsource.resources["get_contacts"].add_limit(15)
