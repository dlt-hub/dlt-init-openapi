from typing import Any, Dict

import pytest

from dlt_openapi.config import Config
from tests.integration.utils import get_indexed_resources

DEFAULT_VALUE = Config().parameter_default_value


@pytest.fixture(scope="module")
def resources() -> Dict[str, Any]:
    return get_indexed_resources("artificial", "params.yml", config=Config(name_resources_by_operation=True))


def test_simple_unresolvable_path_params(resources: Dict[str, Any]) -> None:
    assert resources["simple_unresolvable_path_params"]["endpoint"]["params"] == {
        "param_1": DEFAULT_VALUE,
        "param_2": DEFAULT_VALUE,
    }


def test_simple_unresolvable_transformer_path_params(resources: Dict[str, Any]) -> None:
    assert resources["collections"]["endpoint"]["params"] == {
        "base_id": DEFAULT_VALUE,
    }
    assert resources["single_collection"]["endpoint"]["params"] == {
        "base_id": DEFAULT_VALUE,
        "collection_id": {"type": "resolve", "resource": "collections", "field": "id"},
    }


def test_optional_query_param(resources: Dict[str, Any]) -> None:
    assert resources["optional_query_param"]["endpoint"].get("params") == {}


def test_non_optional_query_param(resources: Dict[str, Any]) -> None:
    assert resources["non_optional_query_param"]["endpoint"]["params"] == {
        "search": DEFAULT_VALUE,
    }


def test_non_optional_query_param_with_pagination(resources: Dict[str, Any]) -> None:
    assert resources["cursor_pagination_1"]["endpoint"]["params"] == {
        "search": DEFAULT_VALUE,
        "path_param": DEFAULT_VALUE,
    }


def test_param_defaults(resources: Dict[str, Any]) -> None:
    assert resources["param_defaults"]["endpoint"]["params"] == {
        "search": "search_default",
        "cursor": DEFAULT_VALUE,
        "path_param": "path_param_default",
        "path_param_2": DEFAULT_VALUE,
    }
