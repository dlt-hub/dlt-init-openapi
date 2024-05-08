from tests.e2e.utils import get_indexed_resources


def test_model_naming() -> None:
    resources = get_indexed_resources("artificial", "naming/entity_naming.yml")
    assert set(resources.keys()) == {"MyModel", "Pokemon", "dog"}


def test_path_naming() -> None:
    resources = get_indexed_resources("artificial", "naming/path_naming.yml")
    assert set(resources.keys()) == {"pokemon_1234", "my_model_1234_other_component", "dogs"}


def test_operation_naming() -> None:
    resources = get_indexed_resources("artificial", "naming/operation_naming.yml")
    assert set(resources.keys()) == {"op.pokemon_1234", "op.my_model_1234", "op.dogs"}
