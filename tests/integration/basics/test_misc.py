from dlt_init_openapi.config import Config
from tests.cases import case_path
from tests.integration.utils import get_detected_project_from_open_api, get_indexed_resources


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


def test_source_template_yields_rest_api_resources() -> None:
    project = get_detected_project_from_open_api(
        case_path("artificial", "pagination.yml"),
        config=Config(name_resources_by_operation=True),
    )
    project.render(dry=True)
    source = project.renderer._render_source()  # type: ignore

    assert "from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources" in source
    assert "yield from rest_api_resources(source_config)" in source
    assert "rest_api_source(" not in source
