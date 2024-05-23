import pytest

from dlt_init_openapi.config import Config
from dlt_init_openapi.exceptions import DltNoEndpointsDiscovered, DltOpenAPINot30Exception, DltUnparseableSpecException
from tests.integration.utils import get_dict_by_case


def test_no_endoint_discovered() -> None:
    with pytest.raises(DltNoEndpointsDiscovered):
        get_dict_by_case("error", "coinpaprika.yaml")


def test_not_openapi_30() -> None:
    with pytest.raises(DltOpenAPINot30Exception):
        get_dict_by_case("error", "art_institute_chicago_api.yaml")

    # if allowed in config, it will work
    get_dict_by_case("error", "art_institute_chicago_api.yaml", config=Config(allow_openapi_2=True))


def test_not_parseable() -> None:
    with pytest.raises(DltUnparseableSpecException):
        get_dict_by_case("error", "malformed_yaml.yaml")
