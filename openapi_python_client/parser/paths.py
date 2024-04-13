from typing import Iterable, Dict, Tuple

import os.path


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
    if not paths:
        return {}
    if len(paths) > 1:
        api_prefix = os.path.commonpath(paths)
        norm_paths = [p.removeprefix(api_prefix) for p in paths]
    else:
        norm_paths = paths

    # Get all path components without slashes and without {parameters}
    split_paths = [[p for p in path.split("/") if p and not p.startswith("{")] for path in norm_paths]

    return {key: "_".join(value) for key, value in zip(paths, split_paths)}


def find_common_prefix(paths: Iterable[Tuple[str, ...]]) -> Tuple[str, ...]:
    paths = list(paths)
    if not paths:
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

    # for path in paths[1:]:
    #     # Compare the current common prefix with the next path
    #     # Truncate the common prefix or keep it as is
    #     common_prefix = [
    #         common_prefix[i] for i in range(min(len(common_prefix), len(path))) if common_prefix[i] == path[i]
    #     ]

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
