# Test different iterations of dotastats spec
#
import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.mark.skip
def test_simple_dotastats_load() -> None:
    api_spec = get_test_case_path("dotastats_with_simple_pagination.yml")
    source = get_dict_from_open_api(api_spec)
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "get_teams",
        "endpoint": {"path": "/teams", "data_selector": "$"},
        # FIXME: No paginator resolved
        # parameters:
        # - name: page
        #   in: query
        #   description: "Page number, zero indexed. Each page returns up to 1000 entries."
        #   required: false
        #   schema:
        #     type: integer
        "paginator": {},
    }

    # source should also work
    dltsource = get_source_from_open_api(api_spec, base_url="https://api.opendota.com/api")
    dltsource.resources["get_teams"].add_limit(15)
