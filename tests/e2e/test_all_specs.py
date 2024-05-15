import pytest
from dlt.common.configuration.exceptions import InvalidNativeValue

from tests.e2e.utils import get_all_spec_paths, get_source

SKIP_CASES = ["zoom_with_pagination.yml"]


@pytest.mark.slow
@pytest.mark.parametrize(
    "case",
    get_all_spec_paths(),
)
def test_all_specs(case: str) -> None:
    for skipped in SKIP_CASES:
        if skipped in case:
            return

    try:
        source = get_source(case)
        assert len(source.resources) >= 1
    except InvalidNativeValue:
        # TODO: remove once core is fixed
        pytest.skip("Skipped for incorrect Basic Auth impl")
