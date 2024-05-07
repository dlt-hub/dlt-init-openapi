from typing import Any, Dict

import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.fixture(scope="module")
def transformers() -> Dict[str, str]:
    case_path = get_test_case_path("transformer_specs.yml")
    # validate that source will work
    get_source_from_open_api(case_path)

    # get dict and save paginator info into dict
    rendered_dict = get_dict_from_open_api(case_path)
    return {
        entry["name"]: entry  # type: ignore
        for entry in rendered_dict["resources"]  # type: ignore
    }


def test_simple_transformer(transformers: Dict[str, Any]) -> None:
    assert transformers["collections"] == {
        "name": "collections",
        "primary_key": "id",
        "endpoint": {"data_selector": "$", "path": "/collection/"},
    }
    assert transformers["single_collection"] == {
        "name": "single_collection",
        "primary_key": "id",
        "endpoint": {
            "data_selector": "$",
            "path": "/collection/{collection_id}",
            "params": {"collection_id": {"type": "resolve", "resource": "collections", "field": "id"}},
        },
    }


def test_match_by_path_var_only(transformers: Dict[str, Any]) -> None:
    assert transformers["users"] == {
        "name": "users",
        "primary_key": "user_id",
        "endpoint": {"data_selector": "$", "path": "/users/"},
    }
    assert transformers["single_user"] == {
        "name": "single_user",
        "primary_key": "user_id",
        "endpoint": {
            "data_selector": "$",
            "path": "/users/{user_id}",
            "params": {"user_id": {"type": "resolve", "resource": "users", "field": "user_id"}},
        },
    }


def test_match_singularized_path(transformers: Dict[str, Any]) -> None:
    assert transformers["invoices"] == {
        "name": "invoices",
        "primary_key": "invoice_id",
        "endpoint": {"data_selector": "$", "path": "/invoices/"},
    }
    assert transformers["single_invoice"] == {
        "name": "single_invoice",
        "primary_key": "invoice_id",
        "endpoint": {
            "data_selector": "$",
            "path": "/invoice/{invoice_id}",
            "params": {"invoice_id": {"type": "resolve", "resource": "invoices", "field": "invoice_id"}},
        },
    }
