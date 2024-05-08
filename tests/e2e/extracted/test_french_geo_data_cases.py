#
# Test different iterations of dotastats spec
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_french_geo_data_load() -> None:
    source = get_dict_by_case("extracted", "french_geo_data_with_pagination.yml")
    assert len(source["resources"]) == 1

    assert source["resources"][0] == {
        "name": "get_regions",
        "endpoint": {"path": "/regions", "data_selector": "$"},
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
