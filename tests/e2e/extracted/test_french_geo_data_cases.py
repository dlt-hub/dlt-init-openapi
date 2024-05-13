#
# Test different iterations of dotastats spec
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip("Does not seem to have the required pagination parameters")
def test_simple_french_geo_data_load() -> None:
    source = get_dict_by_case("extracted", "french_geo_data_with_pagination.yml")
    assert len(source["resources"]) == 1

    # use page query parameter
    assert source["resources"][0] == {
        "name": "Region",
        "endpoint": {
            "data_selector": "$",
            "path": "/regions",
            "paginator": {},
        },
    }
