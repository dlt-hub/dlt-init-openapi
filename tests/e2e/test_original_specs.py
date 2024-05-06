import pytest

from tests.cases import all_local_original_specs, all_repo_original_specs
from tests.e2e.utils import get_source_from_open_api


@pytest.mark.slow
@pytest.mark.parametrize(
    "case",
    all_local_original_specs(),
)
def test_local_original_specs(case: str) -> None:
    source = get_source_from_open_api(case)
    assert len(source.resources) >= 2


@pytest.mark.slow
@pytest.mark.parametrize(
    "case",
    all_repo_original_specs(),
)
def test_repo_original_specs(case: str) -> None:
    if "amazon_kenisis" in case:
        pytest.skip("Fix later")
    source = get_source_from_open_api(case)
    assert len(source.resources) >= 2
