from typing import Dict, Any, cast

import os
import pytest
import importlib
from distutils.dir_util import copy_tree, remove_tree

from openapi_python_client.config import Config
from openapi_python_client.cli import REST_API_SOURCE_LOCATION
from openapi_python_client import _get_project_for_url_or_path

from dlt.extract.source import DltSource

from tests.cases import all_cases


LOCAL_DIR = "tests/_local/"

TOP = """
# type: ignore
# flake8: noqa 
from typing import Any
Oauth20Credentials = Any
"""


def get_rendered_dict_for_openapi(case: str) -> DltSource:
    """
    This function renders the source into a string and returns the extracted
    dict for further inspection
    """
    copy_tree(REST_API_SOURCE_LOCATION, LOCAL_DIR + "rest_api")

    config = Config()
    config.project_name_override = "test"
    config.package_name_override = "test"
    project = _get_project_for_url_or_path(
        url=None, path=case, custom_template_path="../openapi_python_client/template", config=config  # type: ignore
    )
    source = project._render_source()
    source = source.replace("from rest_api", "from .rest_api")

    local = LOCAL_DIR + "temp"
    with open(LOCAL_DIR + "__init__.py", "w") as f:
        f.write("")
    with open(LOCAL_DIR + "temp.py", "w") as f:
        f.write(TOP + source)

    # set some env vars
    os.environ["BASE_URL"] = "base_url"

    module = importlib.import_module(local.replace("/", "."))
    remove_tree(LOCAL_DIR + "rest_api")
    return cast(DltSource, module.test_source())


@pytest.mark.parametrize(
    "case",
    all_cases(),
)
def test_renderer_output_validity(case: str) -> None:
    source = get_rendered_dict_for_openapi(case)
    assert len(source.resources) >= 2
