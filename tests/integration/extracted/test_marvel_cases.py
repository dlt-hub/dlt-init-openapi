#
# Test different iterations of dotastats spec, this is FastAPI generated
#
from tests.integration.utils import get_dict_by_case


def test_marvel() -> None:
    source = get_dict_by_case("extracted", "marvel_with_pagination_and_json_path.yml")
    assert len(source["resources"]) == 1

    assert source["client"]["paginator"] == {
        "limit": 20,
        "limit_param": "limit",
        "offset_param": "offset",
        "total_path": "data.total",
        "type": "offset",
    }

    assert source["resources"][0] == {
        "name": "event",
        "table_name": "event",
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "params": {"characterId": "FILL_ME_IN"},
            "data_selector": "data.results",
            "path": "/v1/public/characters/{characterId}/events",
        },
    }
