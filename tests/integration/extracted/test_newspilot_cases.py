#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.integration.utils import get_dict_by_case


@pytest.mark.skip("wait for page paginator")
def test_teamgpt_load() -> None:
    source = get_dict_by_case("extracted", "newspilot_with_pagination.yml")
    assert len(source["resources"]) == 1

    # FIXME: they use page and articles_per_page query parameters
    assert source["resources"][0] == {
        "name": "article",
        "endpoint": {
            "data_selector": "$",
            "path": "/api/articles/",
            "paginator": {},
        },
    }
