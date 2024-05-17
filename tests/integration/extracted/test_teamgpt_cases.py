#
# Test different iterations of dotastats spec, this is FastAPI generated
#
from tests.integration.utils import get_dict_by_case


def test_teamgpt_load() -> None:
    source = get_dict_by_case("extracted", "teamgpt_with_pagination.yml")
    assert len(source["resources"]) == 1

    assert source["client"]["paginator"] == {
        "maximum_page": 20,
        "page_param": "page",
        "type": "page_number",
        "total_path": "",
    }

    # FIXME: they use page and page_size parameters
    assert source["resources"][0] == {
        "name": "response_get_filesystem_objects_api_companies_uuid_filesystem_objects_get",
        "table_name": "response_get_filesystem_objects_api_companies_uuid_filesystem_objects_get",
        "endpoint": {
            "data_selector": "$",
            "path": "/api/companies/{uuid}/filesystem_objects",
            "params": {"uuid": "FILL_ME_IN"},
        },
    }
