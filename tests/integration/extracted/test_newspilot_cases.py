#
# Test different iterations of dotastats spec, this is FastAPI generated
#

from tests.integration.utils import get_dict_by_case


def test_newspilot_load() -> None:
    source = get_dict_by_case("extracted", "newspilot_with_pagination.yml")
    assert len(source["resources"]) == 1

    assert source["client"]["paginator"] == {
        "maximum_page": 20,
        "page_param": "page",
        "type": "page_number",
    }

    # FIXME: they use page and articles_per_page query parameters
    assert source["resources"][0] == {
        "name": "article",
        "table_name": "article",
        "endpoint": {
            "data_selector": "$",
            "path": "/api/articles/",
        },
    }
