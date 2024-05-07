from typing import List, Tuple

import pytest

from openapi_python_client.utils.paths import (
    find_longest_common_prefix,
    get_non_var_path_parts,
    get_path_parts,
    get_path_var_name,
    get_path_var_names,
    is_path_var,
    path_looks_like_list,
    table_names_from_paths,
)


def test_table_names_from_paths_prefixed() -> None:
    api_paths = [
        "/api/v2/users/{id}",
        "/api/v2/objects/companies",
        "/api/v2/objects/deals",
        "/api/v2/users",
        "/api/v2/objects/deals/activities",
        "/api/v2",
    ]

    result = table_names_from_paths(api_paths)

    assert result == {
        "/api/v2/users/{id}": "users",
        "/api/v2/objects/companies": "objects_companies",
        "/api/v2/objects/deals": "objects_deals",
        "/api/v2/users": "users",
        "/api/v2/objects/deals/activities": "objects_deals_activities",
        "/api/v2": "",
    }


def test_table_names_from_paths_no_prefix() -> None:
    api_paths = [
        "/users/{id}",
        "/objects/companies",
        "/objects/deals",
        "/users",
        "/objects/deals/activities",
        "/",
    ]

    result = table_names_from_paths(api_paths)

    assert result == {
        "/users/{id}": "users",
        "/objects/companies": "objects_companies",
        "/objects/deals": "objects_deals",
        "/users": "users",
        "/objects/deals/activities": "objects_deals_activities",
        "/": "",
    }


@pytest.mark.parametrize(
    "paths, expected",
    [
        (
            [("data", "[*]", "email", "[*]"), ("data", "[*]", "phone", "[*]")],
            ("data", "[*]"),
        ),
        (
            [("a", "b", "c"), ("a", "b", "d"), ("a", "b"), ("a", "b", "c", "d")],
            ("a", "b"),
        ),
        (
            [("a", "b", "c"), ("k", "b"), ("a", "b"), ("a", "b", "c", "d")],
            (),
        ),
        (
            [("a",), ("a", "b"), ("a", "b", "c"), ("a", "b", "d")],
            ("a", "b"),
        ),
    ],
)
def test_find_longest_common_prefix(paths: List[Tuple[str, ...]], expected: Tuple[str, ...]) -> None:
    result = find_longest_common_prefix(paths)
    assert result == expected


def test_get_path_parts() -> None:
    assert get_path_parts("") == []
    assert get_path_parts("/hello//") == ["hello"]
    assert get_path_parts("this/is/my/path") == ["this", "is", "my", "path"]
    assert get_path_parts(" ") == [" "]
    assert get_path_parts("/") == [""]


def test_is_path_var() -> None:
    assert is_path_var("{hello}") is True
    assert is_path_var("{hello") is False
    assert is_path_var("hello") is False
    assert is_path_var("  {hello}  ") is True


def test_get_path_var_name() -> None:
    assert get_path_var_name("no var") is None
    assert get_path_var_name("{my_var}") == "my_var"
    assert get_path_var_name("  {my_var  }") == "my_var"


def test_get_path_var_names() -> None:
    assert get_path_var_names("hello/my/path") == []
    assert get_path_var_names("hello/{var1}/my/path/{var2}") == ["var1", "var2"]


def test_get_non_var_path_parts() -> None:
    assert get_non_var_path_parts("hello/my/path") == ["hello", "my", "path"]
    assert get_non_var_path_parts("hello/{var1}/my/path/{var2}") == ["hello", "my", "path"]


def test_path_looks_like_list() -> None:
    assert path_looks_like_list("") is False
    assert path_looks_like_list("hello/{var1}/my/path/{var2}") is False
    assert path_looks_like_list("hello/{var1}/my/path/") is True
