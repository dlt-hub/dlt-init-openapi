from typing import Any, Dict

import pytest

from tests.e2e.utils import get_indexed_resources


@pytest.fixture(scope="module")
def resources() -> Dict[str, Any]:
    return get_indexed_resources("artificial", "transformer.yml", name_resources_by_operation=True)


def test_simple_transformer(resources: Dict[str, Any]) -> None:
    assert resources["collections"] == {
        "name": "collections",
        "table_name": "collection",
        "primary_key": "id",
        "endpoint": {"data_selector": "$", "path": "/collection/"},
    }
    assert resources["single_collection"] == {
        "name": "single_collection",
        "table_name": "collection",
        "primary_key": "id",
        "endpoint": {
            "data_selector": "$",
            "path": "/collection/{collection_id}",
            "params": {"collection_id": {"type": "resolve", "resource": "collections", "field": "id"}},
        },
    }


def test_match_by_path_var_only(resources: Dict[str, Any]) -> None:
    assert resources["users"] == {
        "name": "users",
        "table_name": "user",
        "primary_key": "user_id",
        "endpoint": {"data_selector": "$", "path": "/users/"},
    }
    assert resources["single_user"] == {
        "name": "single_user",
        "table_name": "user",
        "primary_key": "user_id",
        "endpoint": {
            "data_selector": "$",
            "path": "/users/{user_id}",
            "params": {"user_id": {"type": "resolve", "resource": "users", "field": "user_id"}},
        },
    }


def test_match_singularized_path(resources: Dict[str, Any]) -> None:
    assert resources["invoices"] == {
        "name": "invoices",
        "table_name": "invoice",
        "primary_key": "invoice_id",
        "endpoint": {"data_selector": "$", "path": "/invoices/"},
    }
    assert resources["single_invoice"] == {
        "name": "single_invoice",
        "table_name": "invoice",
        "primary_key": "invoice_id",
        "endpoint": {
            "data_selector": "$",
            "path": "/invoice/{invoice_id}",
            "params": {"invoice_id": {"type": "resolve", "resource": "invoices", "field": "invoice_id"}},
        },
    }
