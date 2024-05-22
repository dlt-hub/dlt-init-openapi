import builtins
import re
from email.message import Message
from importlib import import_module
from keyword import iskeyword
from typing import Any, Dict, Iterable, List, Sequence, TypeVar

DELIMITERS = r"\. _-"

T = TypeVar("T")


class ClassName(str):
    """A PascalCase string which has been validated / transformed into a valid class name for Python"""

    def __new__(cls, value: str, prefix: str) -> "ClassName":
        new_value = fix_reserved_words(pascal_case(sanitize(value)))

        if not new_value.isidentifier():
            value = f"{prefix}{new_value}"
            new_value = fix_reserved_words(pascal_case(sanitize(value)))
        return str.__new__(cls, new_value)

    def __deepcopy__(self, _: Any) -> "ClassName":
        return self


def sanitize(value: str) -> str:
    """Removes every character that isn't 0-9, A-Z, a-z, or a known delimiter"""
    return re.sub(rf"[^\w{DELIMITERS}]+", "", value)


def split_words(value: str) -> List[str]:
    """Split a string on words and known delimiters"""
    # We can't guess words if there is no capital letter
    if any(c.isupper() for c in value):
        value = " ".join(re.split("([A-Z]?[a-z]+)", value))
    return re.findall(rf"[^{DELIMITERS}]+", value)


RESERVED_WORDS = (set(dir(builtins)) | {"self", "true", "false", "datetime"}) - {"type", "id"}


def fix_reserved_words(value: str) -> str:
    """
    Using reserved Python words as identifiers in generated code causes problems, so this function renames them.

    Args:
        value: The identifier to-be that should be renamed if it's a reserved word.

    Returns:
        `value` suffixed with `_` if it was a reserved word.
    """
    if value in RESERVED_WORDS or iskeyword(value):
        return f"{value}_"
    return value


def snake_case(value: str) -> str:
    """Converts to snake_case"""
    if not value:
        return value
    words = split_words(sanitize(value))
    return "_".join(words).lower()


def pascal_case(value: str) -> str:
    """Converts to PascalCase"""
    words = split_words(sanitize(value))
    capitalized_words = (word.capitalize() if not word.isupper() else word for word in words)
    return "".join(capitalized_words)


def kebab_case(value: str) -> str:
    """Converts to kebab-case"""
    words = split_words(sanitize(value))
    return "-".join(words).lower()


def remove_string_escapes(value: str) -> str:
    """Used when parsing string-literal defaults to prevent escaping the string to write arbitrary Python

    **REMOVING OR CHANGING THE USAGE OF THIS FUNCTION HAS SECURITY IMPLICATIONS**

    See Also:
        - https://github.com/openapi-generators/openapi-python-client/security/advisories/GHSA-9x4c-63pf-525f
    """
    return value.replace('"', r"\"")


def get_content_type(content_type: str) -> str:
    """
    Given a string representing a content type with optional parameters, returns the content type only
    """
    message = Message()
    message.add_header("Content-Type", content_type)

    content_type = message.get_content_type()

    return content_type


def count_by_length(items: Iterable[Sequence[Any]]) -> Dict[int, int]:
    """Given a list of sequences, count the number of sequences by length"""
    result: Dict[int, int] = {}

    for key in items:
        length = len(key)
        result[length] = result.get(length, 0) + 1

    return result


def unique_list(items: Sequence[T]) -> List[T]:
    return list({k: None for k in items}.keys())


def import_class_from_string(dotted_path: str) -> object:
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (module_path, class_name)
        raise ImportError(msg)
