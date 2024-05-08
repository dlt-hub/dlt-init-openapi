import pytest

from tests.e2e.utils import get_all_spec_paths, get_source


@pytest.mark.slow
@pytest.mark.parametrize(
    "case",
    get_all_spec_paths(),
)
@pytest.mark.parametrize("skip_case", ["zoom_with_pagination.yml"])
def test_all_specs(case: str, skip_case: str) -> None:
    if skip_case in case:
        return

    source = get_source(case)
    assert len(source.resources) >= 1
