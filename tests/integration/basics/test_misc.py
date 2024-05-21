from dlt_init_openapi.config import Config
from tests.integration.utils import get_indexed_resources


def test_endpoint_selection() -> None:
    """test filer for endpoints"""
    # we use some file, does not matter which one
    resources = get_indexed_resources("artificial", "pagination.yml", config=Config(name_resources_by_operation=True))

    # this is the default file wo filtering
    base_keys = list(resources.keys())
    assert len(base_keys) > 4

    # only keep two
    filtered_resources = get_indexed_resources(
        "artificial",
        "pagination.yml",
        config=Config(name_resources_by_operation=True, endpoint_filter=lambda _c: {base_keys[0], base_keys[3]}),
    )
    assert len(filtered_resources.keys()) == 2
    assert list(filtered_resources.keys()) == [base_keys[0], base_keys[3]]
