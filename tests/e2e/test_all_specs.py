import pytest

from tests.e2e.utils import get_all_spec_paths, get_source


@pytest.mark.slow
@pytest.mark.parametrize(
    "case",
    get_all_spec_paths(),
)
def test_all_specs(case: str) -> None:
    source = get_source(case)
    assert len(source.resources) >= 1
