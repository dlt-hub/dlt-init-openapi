import os
from typing import Iterable


ORIGINAL_SPECS_FOLDERS = "original_specs"
TEST_SPECS_FOLDER = "test_specs"
ALL_ORIGINAL_SPECS = ["spotify.json", "dummyapi.yml", "pokeapi.yml"]


def case_path(case: str) -> str:
    return os.path.join(os.path.dirname(__file__), case)


def get_original_case_path(case: str) -> str:
    return case_path(os.path.join(ORIGINAL_SPECS_FOLDERS, case))


def get_test_case_path(case: str) -> str:
    return case_path(os.path.join(TEST_SPECS_FOLDER, case))


def all_original_specs() -> Iterable[str]:
    for case in ALL_ORIGINAL_SPECS:
        yield get_original_case_path(case)
