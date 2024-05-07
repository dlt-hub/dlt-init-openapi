"""General purpose utils"""
from typing import List

import inflector  # type: ignore

inf = inflector.English()


def get_word_variations(word: str) -> List[str]:
    """builds variations of a word for better pk resolution"""
    result = {word}
    result.add(inf.pluralize(word))
    result.add(inf.singularize(word))
    return list(result)
