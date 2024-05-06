from typing import Any, Dict

import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.fixture(scope="module")
def data_selectors() -> Dict[str, str]:
    case_path = get_test_case_path("content_path_specs.yml")
    # validate that source will work
    get_source_from_open_api(case_path)

    # get dict and save paginator info into dict
    rendered_dict = get_dict_from_open_api(case_path)
    return {
        entry["name"]: entry.get("endpoint").get("data_selector")  # type: ignore
        for entry in rendered_dict["resources"]  # type: ignore
    }


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
