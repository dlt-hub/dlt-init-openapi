from typing import Any, Dict

import pytest

from tests.e2e.utils import get_indexed_resources


@pytest.fixture(scope="module")
def paginators() -> Dict[str, Any]:
    resources = get_indexed_resources("artificial", "pagination.yml", name_resources_by_operation=True)
    return {name: resource.get("endpoint").get("paginator") for name, resource in resources.items()}  # type: ignore


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
