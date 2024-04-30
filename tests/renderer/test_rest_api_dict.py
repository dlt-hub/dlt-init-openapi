import pytest


from tests.renderer.utils import get_source_from_open_api
from tests.cases import all_original_specs


@pytest.mark.parametrize(
    "case",
    all_original_specs(),
)
def test_renderer_output_validity(case: str) -> None:
    source = get_source_from_open_api(case)
    assert len(source.resources) >= 2
