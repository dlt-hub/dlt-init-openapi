from typing import Any, Dict

import pytest

from tests.e2e.utils import get_indexed_resources


@pytest.fixture(scope="module")
def data_selectors() -> Dict[str, str]:
    resources = get_indexed_resources("artificial", "data_selector.yml", force_operation_naming=True)
    return {name: resource.get("endpoint").get("data_selector") for name, resource in resources.items()}  # type: ignore


def test_unnested_collection_result(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["unnested_collection_result"] == "$"


def test_results_collection_json_path(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["results_collection_json_path"] == "results"


def test_results_collection_with_inner_list_json_path(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["test_results_collection_with_inner_list_json_path"] == "results"


def test_nested_results_collection_json_path(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["nested_results_collection_json_path"] == "content.results"


def test_single_object_unneested(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["single_object_unnested"] == "$"


def test_single_object_nested(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["single_object_nested"] == "result_object"


def test_platform_nested(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["get_workspace_run_workspace__workspace_id__run__transaction_id__get"] == "$"


def test_expect_list_but_no_list_and_no_types(data_selectors: Dict[str, Any]) -> None:
    assert data_selectors["expect_list_but_no_list_and_no_types"] == "$"
