import os


def case_path(fn: str) -> str:
    return os.path.join(os.path.dirname(__file__), fn)
