import importlib
import os
from distutils.dir_util import copy_tree, remove_tree
from typing import Literal, Union, cast

from dlt.common.validation import validate_dict
from dlt.extract.source import DltSource

from openapi_python_client import _get_project_for_url_or_path
from openapi_python_client.cli import REST_API_SOURCE_LOCATION
from openapi_python_client.config import Config
from sources.sources.rest_api.typing import RESTAPIConfig

LOCAL_DIR = "tests/_local/"


def get_source_or_dict_from_open_api(
    case: str, rt: Literal["source", "dict"] = "source", base_url: str = "base_url", force_operation_naming: bool = True
) -> Union[DltSource, RESTAPIConfig]:
    """
    This function renders the source into a string and returns the extracted
    dict for further inspection
    """
    copy_tree(REST_API_SOURCE_LOCATION, LOCAL_DIR + "rest_api")

    TOP = """
# type: ignore
# flake8: noqa 
from typing import Any
Oauth20Credentials = Any
"""

    config = Config()
    config.project_name_override = "test"
    config.package_name_override = "test"
    project = _get_project_for_url_or_path(
        url=None, path=case, custom_template_path="../openapi_python_client/template", config=config, force_operation_naming=force_operation_naming  # type: ignore
    )
    source = project._render_source()

    if rt == "dict":
        source = source.replace('@dlt.source(name="test_source", max_table_nesting=2)', "")
        source = source.replace("rest_api_source(source_config)", "source_config")
        source = source.replace("dlt.secrets.value", '"SECRET_VALUE"')

    source = source.replace("from rest_api", "from .rest_api")
    basename = os.path.basename(case).split(".")[0] + "_" + rt

    local = LOCAL_DIR + basename
    with open(LOCAL_DIR + "__init__.py", "w") as f:
        f.write("")
    with open(local + ".py", "w") as f:
        f.write(TOP + source)

    # set some env vars
    os.environ["BASE_URL"] = base_url
    os.environ["CREDENTIALS"] = "1234"
    os.environ["TOKEN"] = "some token"
    os.environ["PASSWORD"] = "some password"
    os.environ["API_KEY"] = "some api key"

    module = importlib.import_module(local.replace("/", "."))

    remove_tree(LOCAL_DIR + "rest_api")

    return cast(DltSource, module.test_source())


def get_source_from_open_api(case: str, base_url: str = "base_url", force_operation_naming: bool = False) -> DltSource:
    return cast(
        DltSource,
        get_source_or_dict_from_open_api(case, "source", base_url, force_operation_naming=force_operation_naming),
    )


def get_dict_from_open_api(case: str, validate: bool = True, force_operation_naming: bool = True) -> RESTAPIConfig:
    api_dict = cast(
        RESTAPIConfig, get_source_or_dict_from_open_api(case, "dict", force_operation_naming=force_operation_naming)
    )
    api_dict["client"]["base_url"] = "something"
    if validate:
        validate_dict(RESTAPIConfig, api_dict, path=".")
    return api_dict
