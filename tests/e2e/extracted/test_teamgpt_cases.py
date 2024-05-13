#
# Test different iterations of dotastats spec, this is FastAPI generated
#
from tests.e2e.utils import get_dict_by_case


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
            "paginator": {
                "limit": 100,
                "limit_param": "page_size",
                "maximum_offset": 20,
                "offset_param": "page",
                "type": "offset",
            },
        },
    }
