from typing import Any, Dict

import pytest

from tests.e2e.utils import get_indexed_resources


@pytest.fixture(scope="module")
def resources() -> Dict[str, Any]:
    return get_indexed_resources("artificial", "primary_key.yml", name_resources_by_operation=True)


def test_primary_key_no_reference(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_no_reference"]["primary_key"] == "id"


def test_primary_key_reference(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_reference"]["primary_key"] == "id"


def test_primary_key_no_type(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_no_type"]["primary_key"] == "id"


def test_primary_key_by_modelname_id(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_by_modelname_id"]["primary_key"] == "mymodel_id"


def test_no_primary_key(resources: Dict[str, Any]) -> None:
    assert resources["no_primary_key"].get("primary_key") is None


def test_primary_key_by_path_component(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_by_path_component"]["primary_key"] == "user_id"


def test_primary_key_by_path_variable(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_by_path_variable"]["primary_key"] == "person_id"


def test_primary_key_from_pluralized_path_component(resources: Dict[str, Any]) -> None:
    assert resources["primary_key_from_pluralized_path_component"]["primary_key"] == "account_id"
