from typing import List, Optional

from openapi_python_client.utils import paths

from .const import PRIMARY_KEY_SUFFIXES, PRIMARY_KEY_WORD_SEPARATORS, PRIMAY_KEY_NAMES
from .utils import get_word_variations


def detect_primary_key_by_name(
    candidates: List[str], model_name: Optional[str] = None, path: Optional[str] = None
) -> str:
    """Try to discover the primary key by name, take into account modelname and path"""

    # build a list of probable names, starting with hardcorded values
    probable_names = [*PRIMAY_KEY_NAMES]

    # last path var is a good probably name
    # TODO: maybe only use it if we think it is not a collection endpoint?
    if path_vars := paths.get_path_var_names(path):
        probable_names.append(path_vars[-1])

    # gather some words from model name and url and create variations
    words = []

    # model name is a good hint
    if model_name:
        words.extend(get_word_variations(model_name))

    # last non path var element is a good basename
    # TODO: maybe only take if we think this is a collection endpoint?
    if non_var_parts := paths.get_non_var_path_parts(path):
        words.extend(get_word_variations(non_var_parts[-1]))

    # build primary key candidates
    for word in words:
        for suffix in PRIMARY_KEY_SUFFIXES:
            for separator in PRIMARY_KEY_WORD_SEPARATORS:
                probable_names.append(f"{word}{separator}{suffix}")
                probable_names.append(f"{suffix}{separator}{word}")

    for pname in probable_names:
        for candidate in candidates:
            if candidate.lower() == pname.lower():
                return candidate

    return None
