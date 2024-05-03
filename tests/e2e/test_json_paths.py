from typing import Dict, Any

import pytest

from tests.e2e.utils import get_source_from_open_api, get_dict_from_open_api
from tests.cases import get_test_case_path


@pytest.fixture(scope="module")
def paginators() -> Dict[str, str]:
    case_path = get_test_case_path("content_path_specs.yml")
    # validate that source will work
    get_source_from_open_api(case_path)

    # get dict and save paginator info into dict
    rendered_dict = get_dict_from_open_api(case_path)
    return {
        entry["name"]: entry.get("endpoint").get("data_selector")  # type: ignore
        for entry in rendered_dict["resources"]  # type: ignore
    }


def test_unnested_collection_result(paginators: Dict[str, Any]) -> None:
    assert paginators["unnested_collection_result"] == "$"


def test_results_collection_json_path(paginators: Dict[str, Any]) -> None:
    assert paginators["results_collection_json_path"] == "results"


def test_nested_results_collection_json_path(paginators: Dict[str, Any]) -> None:
    assert paginators["nested_results_collection_json_path"] == "content.results"


def test_single_object_unneested(paginators: Dict[str, Any]) -> None:
    assert paginators["single_object_unnested"] == "$"


def test_single_object_nested(paginators: Dict[str, Any]) -> None:
    assert paginators["single_object_nested"] == "result_object"
