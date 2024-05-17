import os.path
from typing import Dict, Iterable, List, Optional, Tuple


def table_names_from_paths(paths: Iterable[str]) -> Dict[str, str]:
    """Try to extract a suitable table name from endpoint paths.

    This function should be called with paths of ALL endpoints in the spec.

    E.g. `/api/v2/users/{id}` -> `users`

    Returns:
        dict of `{<path>: <table_name>}`
    """
    # Remove common prefix for endpoints. For example  all paths might
    # start with /api/v2 and we don't want this to be part of the name
    paths = list(paths)
    if not (paths := list(paths)):
        return {}

    # normalize paths
    api_prefix = os.path.commonpath(paths)
    norm_paths = [p.removeprefix(api_prefix) for p in paths]

    # Get all path components without slashes and without {parameters}
    split_paths = [get_non_var_path_parts(path) for path in norm_paths]

    return {key: "_".join(value) for key, value in zip(paths, split_paths)}


def find_common_prefix(paths: Iterable[Tuple[str, ...]]) -> Tuple[str, ...]:
    if not (paths := list(paths)):
        return ()

    common_prefix = list(paths[0])

    for path in paths[1:]:
        # Initialize a new prefix list for comparison results
        new_prefix = []
        for i in range(min(len(common_prefix), len(path))):
            if common_prefix[i] == path[i]:
                new_prefix.append(common_prefix[i])
            else:
                # As soon as a mismatch is found, break the loop
                break
        common_prefix = new_prefix

    return tuple(common_prefix)


def find_longest_common_prefix(paths: Iterable[Tuple[str, ...]]) -> Tuple[str, ...]:
    """Given a list of path tuples, return the longest prefix
    that is common to all of them. This may be the root path which is simply
    an empty tuple.

    For example:
    >>> find_longest_common_prefix([("a", "b", "c"), ("a", "b", "d"), ("a", "b"), ("a", "b", "c", "d")])
    ('a', 'b')

    >>> find_longest_common_prefix([("a", "b", "c"), ("k", "b"), ("a", "b"), ("a", "b", "c", "d")])
    ()

    >>> find_longest_common_prefix(("a",), ("a", "b"), ("a", "b", "c"), ("a", "b", "d"))
    ("a", "b")

    >>> find_longest_common_prefix({('data', '[*]', 'email', '[*]'), ('data', '[*]', 'phone', '[*]')})
    ("data", "[*]")
    """
    paths = set(paths)

    if not paths:
        return ()

    prefix = find_common_prefix(paths)
    while True:
        # Do multiple passes to find the most nested prefix
        paths.discard(prefix)
        longer_prefix = find_common_prefix(paths)

        if not longer_prefix or longer_prefix == prefix:
            break
        prefix = longer_prefix

    return prefix


def get_path_parts(path: str) -> List[str]:
    """convert path into parts"""
    if not path:
        return []
    path = path.split(".")[0]
    return path.strip("/").split("/")


def is_path_var(part: str) -> bool:
    """check if a part is path var"""
    part = part.strip()
    return len(part) > 1 and part[0] == "{" and part[-1] == "}"


def get_path_var_name(part: str) -> Optional[str]:
    """extract var name from path part"""
    if not is_path_var(part):
        return None
    return part.strip()[1:-1].strip()


def get_path_var_names(path: str) -> List[str]:
    """get all path var names in order"""
    return [get_path_var_name(part) for part in get_path_parts(path) if is_path_var(part)]


def get_non_var_path_parts(path: str) -> List[str]:
    """get all parts of a path that are not vars"""
    return [part for part in get_path_parts(path) if not is_path_var(part)]


def path_looks_like_list(path: str) -> bool:
    """check to see if we think the path may be a list endpoint"""
    if not (parts := get_path_parts(path)):
        return False
    # if the last path part is not var, this could be a list
    return not is_path_var(parts[-1])
