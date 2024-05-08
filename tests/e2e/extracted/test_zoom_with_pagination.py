#
# Test different iterations of dotastats spec
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_zoom_load() -> None:
    source = get_dict_by_case("extracted", "zoom_with_pagination.yml")

    assert len(source["resources"]) == 2

    # FIXME: this spec defines schema right in the endpoints
    # pydantic.error_wrappers.ValidationError: 2 validation errors for OpenAPI
    # paths -> /contacts -> get -> responses -> 200 -> description
    #   field required (type=value_error.missing)
    # paths -> /contacts -> get -> responses -> 200 -> $ref
    #   field required (type=value_error.missing)

    # uses next_page_token query parameter for pagination
    assert source["resources"][0] == {
        "name": "get_accounts",
        "endpoint": {
            "path": "/accounts",
            "data_selector": "$",
            "paginator": {},
        },
    }
