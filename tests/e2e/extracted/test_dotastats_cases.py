# Test different iterations of dotastats spec
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_simple_dotastats_load() -> None:
    source = get_dict_by_case("extracted", "dotastats_with_simple_pagination.yml")
    assert len(source["resources"]) == 1

    # use page query parameter
    assert source["resources"][0] == {
        "name": "get_teams",
        "endpoint": {
            "path": "/teams",
            "data_selector": "$",
            "paginator": {},
        },
    }
