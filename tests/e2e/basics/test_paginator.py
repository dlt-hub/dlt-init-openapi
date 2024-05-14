from typing import Any, Dict

import pytest

from tests.e2e.utils import get_indexed_resources


@pytest.fixture(scope="module")
def paginators() -> Dict[str, Any]:
    resources = get_indexed_resources("artificial", "pagination.yml", name_resources_by_operation=True)
    return {name: resource.get("endpoint").get("paginator") for name, resource in resources.items()}  # type: ignore


def test_offset_limit_pagination_1(paginators: Dict[str, Any]) -> None:
    assert paginators["offset_limit_pagination_1"] == {
        "limit": 20,
        "limit_param": "limit",
        "offset_param": "offset",
        "type": "offset",
        "total_path": "count",
    }


def test_offset_limit_pagination_no_count_1(paginators: Dict[str, Any]) -> None:
    assert paginators["offset_limit_pagination_no_count_1"] == {
        "limit": 20,
        "limit_param": "limit",
        "offset_param": "offset",
        "type": "offset",
        "maximum_offset": 20,
    }


def test_json_links_pagination_1(paginators: Dict[str, Any]) -> None:
    assert paginators["json_links_pagination_1"] == {
        "next_url_path": "next",
        "type": "json_response",
    }


def test_json_cursor_1(paginators: Dict[str, Any]) -> None:
    assert paginators["cursor_pagination_1"] == {"cursor_param": "cursor", "cursor_path": "cursor", "type": "cursor"}


def test_page_number_paginator_no_count(paginators: Dict[str, Any]) -> None:
    assert paginators["page_number_paginator_no_count"] == {
        "type": "page_number",
        "page_param": "page",
        "maximum_page": 20,
    }


def test_page_number_paginator_with_count(paginators: Dict[str, Any]) -> None:
    assert paginators["page_number_paginator_with_count"] == {
        "type": "page_number",
        "page_param": "page",
        "total_path": "count",
    }
