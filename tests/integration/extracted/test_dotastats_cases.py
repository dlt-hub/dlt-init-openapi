# Test different iterations of dotastats spec
#

from tests.integration.utils import get_dict_by_case


def test_simple_dotastats_load() -> None:
    source = get_dict_by_case("extracted", "dotastats_with_simple_pagination.yml")
    assert len(source["resources"]) == 1

    assert source["client"]["paginator"] == {
        "maximum_page": 20,
        "page_param": "page",
        "type": "page_number",
        "total_path": "",
    }

    # use page query parameter
    assert source["resources"][0] == {
        "name": "team",
        "table_name": "team",
        "endpoint": {
            "path": "/teams",
            "data_selector": "$",
        },
    }
