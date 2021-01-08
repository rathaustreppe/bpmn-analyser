import os


def rel_to_abs_path(rel_path: str) -> str:
    """
    Takes a path and returns it as an absolute path.
    If the given path is absolute already, it returns the unchanged path.
    """
    if not os.path.isabs(rel_path):
        abs_path = os.path.abspath(rel_path)
        return abs_path
    else:
        abs_path = rel_path
        return abs_path