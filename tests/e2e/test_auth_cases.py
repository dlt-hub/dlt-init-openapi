from tests.e2e.utils import get_dict_from_open_api, get_source_from_open_api
from tests.cases import get_auth_case_path


def test_bearer_auth() -> None:
    auth_case = get_auth_case_path("bearer_token_auth.yml")
    source_dict = get_dict_from_open_api(auth_case)
    assert source_dict["client"]["auth"] == {"type": "http", "scheme": "bearer", "token": None}
    get_source_from_open_api(auth_case)


def test_api_key_auth() -> None:
    auth_case = get_auth_case_path("api_key_auth.yml")
    source_dict = get_dict_from_open_api(auth_case)
    assert source_dict["client"]["auth"] == {
        "type": "apiKey",
        "api_key": None,
        "name": "X-API-KEY",
        "location": "header",
    }
    get_source_from_open_api(auth_case)


def test_basic_auth() -> None:
    auth_case = get_auth_case_path("basic_auth.yml")
    source_dict = get_dict_from_open_api(auth_case)
    assert source_dict["client"]["auth"] == {"type": "http", "scheme": "basic", "username": "", "password": None}
    get_source_from_open_api(auth_case)
