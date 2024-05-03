from typing import Dict, Any

import pytest

from tests.e2e.utils import get_source_from_open_api, get_dict_from_open_api
from tests.cases import get_test_case_path


@pytest.fixture(scope="module")
def paginators() -> Dict[str, Any]:
    case_path = get_test_case_path("pagination_specs.yml")
    # validate that source will work
    get_source_from_open_api(case_path)

    # get dict and save paginator info into dict
    rendered_dict = get_dict_from_open_api(case_path)
    return {
        entry["name"]: entry.get("endpoint").get("paginator") for entry in rendered_dict["resources"]  # type: ignore
    }


def test_offset_limit_pagination_1(paginators: Dict[str, Any]) -> None:
    assert paginators["offset_limit_pagination_1"] == {
        "initial_limit": 20,
        "limit_param": "limit",
        "offset_param": "offset",
        "type": "offset",
        "total_path": "count",
    }


def test_json_links_pagination_1(paginators: Dict[str, Any]) -> None:
    assert paginators["json_links_pagination_1"] == {
        "next_url_path": "next",
        "type": "json_links",
    }


def test_json_cursor_1(paginators: Dict[str, Any]) -> None:
    assert paginators["cursor_pagination_1"] == {"cursor_param": "cursor", "cursor_path": "cursor", "type": "cursor"}
