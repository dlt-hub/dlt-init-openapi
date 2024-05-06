from typing import Any, Dict

import pytest

from tests.cases import get_test_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


@pytest.fixture(scope="module")
def transformers() -> Dict[str, str]:
    case_path = get_test_case_path("primary_key_specs.yml")
    # validate that source will work
    get_source_from_open_api(case_path)

    # get dict and save paginator info into dict
    rendered_dict = get_dict_from_open_api(case_path)
    return {
        entry["name"]: entry  # type: ignore
        for entry in rendered_dict["resources"]  # type: ignore
    }


def test_primary_key_no_reference(transformers: Dict[str, Any]) -> None:
    assert transformers["primary_key_no_reference"]["primary_key"] == "id"


def test_primary_key_reference(transformers: Dict[str, Any]) -> None:
    assert transformers["primary_key_reference"]["primary_key"] == "id"


def test_primary_key_no_type(transformers: Dict[str, Any]) -> None:
    assert transformers["primary_key_no_type"]["primary_key"] == "id"
