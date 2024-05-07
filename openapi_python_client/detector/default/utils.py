"""General purpose utils"""
from typing import List

import inflector  # type: ignore

from openapi_python_client.utils import paths

inf = inflector.English()


def get_word_variations(word: str) -> List[str]:
    """builds variations of a word for better pk resolution"""
    result = {word}
    result.add(inf.pluralize(word))
    result.add(inf.singularize(word))
    return list(result)


def singularized_path_parts(path: str) -> List[str]:
    path_parts = paths.get_path_parts(path)
    return [inf.singularize(p) if not paths.is_path_var(p) else p for p in path_parts]
