from typing import Dict, Any
import pytest
import importlib

from tests.cases import all_cases
from openapi_python_client.config import Config

from openapi_python_client import _get_project_for_url_or_path
from dlt.common.validation import validate_dict
from sources.sources.rest_api.typing import RESTAPIConfig


def get_rendered_dict_for_openapi(case: str) -> Dict[Any, Any]:
    """
    This function renders the source into a string and returns the extracted
    dict for further inspection
    """
    config = Config()
    config.project_name_override = "test"
    config.package_name_override = "test"
    project = _get_project_for_url_or_path(
        url=None, path=case, custom_template_path="../openapi_python_client/template", config=config  # type: ignore
    )
    source = project._render_source().splitlines()
    cutoff = 0
    for line in source:
        cutoff += 1
        if line.startswith("@dlt"):
            break

    TOP = """
from typing import Any, List
DltResource = Any
Oauth20Credentials = Any
def rest_api_source(input):
    return input
"""

    source = source[cutoff:]
    source_j = "\n".join(source)
    source_j = source_j.replace("dlt.secrets.value", '"secret"')
    source_j = source_j.replace("dlt.config.value", '"secret"')

    with open("temp.py", "w") as f:
        f.write(TOP + source_j)

    module = importlib.import_module("temp")
    return module.test_source()


@pytest.mark.parametrize(
    "case",
    all_cases(),
)
def test_renderer_output_validity(case: str) -> None:
    d = get_rendered_dict_for_openapi(case)
    validate_dict(RESTAPIConfig, d, ".")
