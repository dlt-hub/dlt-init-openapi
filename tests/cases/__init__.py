import os
from typing import Iterable

ORIGINAL_SPECS_FOLDERS = "./tests/cases/original_specs"
TEST_SPECS_FOLDER = "./tests/cases/test_specs"
REPO_SPECS_FOLDER = "./tests/cases/original_specs"
AUTH_SPECS_FOLDER = "./tests/cases/auth_specs"
NAMING_SPECS_FOLDER = "./tests/cases/naming_specs"


def case_path(case: str) -> str:
    return os.path.join(os.path.dirname(__file__), case)


def get_original_case_path(case: str) -> str:
    return os.path.join(ORIGINAL_SPECS_FOLDERS, case)


def get_auth_case_path(case: str) -> str:
    return os.path.join(AUTH_SPECS_FOLDER, case)


def get_naming_case_path(case: str) -> str:
    return os.path.join(NAMING_SPECS_FOLDER, case)


def get_test_case_path(case: str) -> str:
    return os.path.join(TEST_SPECS_FOLDER, case)


def get_repo_case_path(case: str) -> str:
    return os.path.join(REPO_SPECS_FOLDER, case)


# todo: we might not need this anymore now that we have this repo
def all_local_original_specs() -> Iterable[str]:
    for item in os.listdir(ORIGINAL_SPECS_FOLDERS):
        yield get_original_case_path(item)


def all_repo_original_specs() -> Iterable[str]:
    for item in os.listdir(REPO_SPECS_FOLDER):
        yield get_repo_case_path(item)
