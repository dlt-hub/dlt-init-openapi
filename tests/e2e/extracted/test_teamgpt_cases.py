#
# Test different iterations of dotastats spec, this is FastAPI generated
#
import pytest

from tests.e2e.utils import get_dict_by_case


@pytest.mark.skip
def test_teamgpt_load() -> None:
    source = get_dict_by_case("extracted", "teamgpt_with_pagination.yml")
    assert len(source["resources"]) == 1

    # FIXME: they use page and page_size parameters
    assert source["resources"][0] == {
        "name": "Response Get Filesystem Objects Api Companies  Uuid  Filesystem Objects Get",
        "endpoint": {
            "data_selector": "$",
            "path": "/api/companies/{uuid}/filesystem_objects",
            "params": {"uuid": "FILL_ME_IN"},
            "paginator": {},
        },
    }
