from typing import Any, Dict

import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api

DEFAULT_VALUE = "FILL_ME_IN"


@pytest.fixture(scope="module")
def path_params() -> Dict[str, str]:
    case_path = get_test_case_path("path_param_specs.yml")
    # validate that source will work
    get_source_from_open_api(case_path)

    # get dict and save paginator info into dict
    rendered_dict = get_dict_from_open_api(case_path)
    return {
        entry["name"]: entry  # type: ignore
        for entry in rendered_dict["resources"]  # type: ignore
    }


def test_simple_unresolvable_path_params(path_params: Dict[str, Any]) -> None:
    assert path_params["simple_unresolvable_path_params"]["endpoint"]["params"] == {
        "param_1": DEFAULT_VALUE,
        "param_2": DEFAULT_VALUE,
    }


def test_simple_unresolvable_transformer_path_params(path_params: Dict[str, Any]) -> None:
    assert path_params["collections"]["endpoint"]["params"] == {
        "base_id": DEFAULT_VALUE,
    }
    assert path_params["single_collection"]["endpoint"]["params"] == {
        "base_id": DEFAULT_VALUE,
        "collection_id": {"type": "resolve", "resource": "collections", "field": "id"},
    }


def test_optional_query_param(path_params: Dict[str, Any]) -> None:
    assert path_params["optional_query_param"]["endpoint"].get("params") is None


def test_non_optional_query_param(path_params: Dict[str, Any]) -> None:
    assert path_params["non_optional_query_param"]["endpoint"]["params"] == {
        "search": DEFAULT_VALUE,
    }


def test_non_optional_query_param_with_pagination(path_params: Dict[str, Any]) -> None:
    assert path_params["cursor_pagination_1"]["endpoint"]["params"] == {
        "search": DEFAULT_VALUE,
        "path_param": DEFAULT_VALUE,
    }
