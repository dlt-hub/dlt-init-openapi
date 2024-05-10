import pytest

from dlt_openapi.config import Config
from dlt_openapi.detector.base_detector import GLOBAL_WARNING_KEY
from dlt_openapi.detector.default.warnings import UnsupportedSecuritySchemeWarning
from tests.integration.utils import get_dict_by_case, get_project_by_case


def test_bearer_auth() -> None:
    source_dict = get_dict_by_case(
        "artificial", "auth/bearer_token_auth.yml", config=Config(name_resources_by_operation=True)
    )
    assert source_dict["client"]["auth"] == {"type": "bearer", "token": "SECRET_VALUE"}


def test_api_key_auth() -> None:
    source_dict = get_dict_by_case("artificial", "auth/api_key_auth.yml")
    assert source_dict["client"]["auth"] == {
        "type": "api_key",
        "api_key": "SECRET_VALUE",
        "name": "X-API-KEY",
        "location": "header",
    }


def test_basic_auth() -> None:
    source_dict = get_dict_by_case("artificial", "auth/basic_auth.yml")
    assert source_dict["client"]["auth"] == {
        "type": "http_basic",
        "username": "username",
        "password": "SECRET_VALUE",
    }


def test_unused_auth() -> None:
    source_dict = get_dict_by_case("artificial", "auth/basic_auth_not_used.yml")
    assert not source_dict["client"].get("auth")


def test_oauth_warning() -> None:
    source_dict = get_dict_by_case("artificial", "auth/oauth.yml")
    assert not source_dict["client"].get("auth")
    project = get_project_by_case("artificial", "auth/oauth.yml")

    # check if the warnings exist that we expect
    warnings = project.detector.get_warnings()

    # no global warnings
    assert len(warnings.get(GLOBAL_WARNING_KEY)) == 1
    assert type(warnings.get(GLOBAL_WARNING_KEY)[0]) == UnsupportedSecuritySchemeWarning


@pytest.mark.parametrize(
    "spec",
    [
        "fastsaverapi.yml",
        "mihomo.yml",
        "geosphere.yml",
        "geosphere.yml",
        "pollenrapporten.yml",
        "planetarycomputer.yml",
    ],
)
def test_no_auth_specs(spec):
    source_dict = get_dict_by_case("original", spec)
    assert "auth" not in source_dict["client"]
