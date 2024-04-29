import os
from typing import Iterable


ALL_CASES = ["dummyapi.yml", "pokeapi.yml", "spotify.json"]


def case_path(fn: str) -> str:
    return os.path.join(os.path.dirname(__file__), fn)


def all_cases() -> Iterable[str]:
    for case in ALL_CASES:
        yield case_path(case)
