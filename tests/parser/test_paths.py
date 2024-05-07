from typing import List, Tuple

import pytest

from openapi_python_client.utils.paths import find_longest_common_prefix, table_names_from_paths


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
