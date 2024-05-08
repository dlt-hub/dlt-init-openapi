import os

ORIGINAL_SPECS_FOLDERS = "./tests/cases/original_specs"
TEST_SPECS_FOLDER = "./tests/cases/test_specs"
REPO_SPECS_FOLDER = "./tests/cases/original_specs"
AUTH_SPECS_FOLDER = "./tests/cases/auth_specs"
NAMING_SPECS_FOLDER = "./tests/cases/naming_specs"


PREFIX = "./tests/cases"

CASE_FOLDERS = {"original": "original_specs", "artificial": "artificial_specs", "extracted": "extracted_specs"}


def case_path(type: str, case: str) -> str:
    folder = CASE_FOLDERS[type]
    return os.path.join(os.path.dirname(__file__), folder, case)
