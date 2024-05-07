from tests.cases import get_naming_case_path
from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api


def test_model_naming() -> None:
    auth_case = get_naming_case_path("entity_naming_spec.yml")
    source_dict = get_dict_from_open_api(auth_case, force_operation_naming=False)
    assert [r["name"] for r in source_dict["resources"]] == ["Pokemon", "MyModel", "dog"]  # type: ignore
    get_source_from_open_api(auth_case)


def test_path_naming() -> None:
    auth_case = get_naming_case_path("path_naming_spec.yml")
    source_dict = get_dict_from_open_api(auth_case, force_operation_naming=False)
    assert [r["name"] for r in source_dict["resources"]] == (  # type: ignore
        ["pokemon_1234", "my_model_1234_other_component", "dogs"]
    )
    get_source_from_open_api(auth_case)


def test_operation_naming() -> None:
    auth_case = get_naming_case_path("operation_naming_spec.yml")
    source_dict = get_dict_from_open_api(auth_case, force_operation_naming=False)
    assert [r["name"] for r in source_dict["resources"]] == (  # type: ignore
        ["op.pokemon_1234", "op.my_model_1234", "op.dogs"]
    )
    get_source_from_open_api(auth_case)
