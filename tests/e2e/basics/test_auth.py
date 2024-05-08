from tests.e2e.utils import get_dict_by_case


def test_bearer_auth() -> None:
    source_dict = get_dict_by_case("artificial", "auth/bearer_token_auth.yml", force_operation_naming=True)
    assert source_dict["client"]["auth"] == {"type": "http", "scheme": "bearer", "token": "SECRET_VALUE"}


def test_api_key_auth() -> None:
    source_dict = get_dict_by_case("artificial", "auth/api_key_auth.yml")
    assert source_dict["client"]["auth"] == {
        "type": "apiKey",
        "api_key": "SECRET_VALUE",
        "name": "X-API-KEY",
        "location": "header",
    }


def test_basic_auth() -> None:
    source_dict = get_dict_by_case("artificial", "auth/basic_auth.yml")
    assert source_dict["client"]["auth"] == {
        "type": "http",
        "scheme": "basic",
        "username": "",
        "password": "SECRET_VALUE",
    }
