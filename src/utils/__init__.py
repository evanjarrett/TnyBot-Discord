import os

from .config import Config


def full_path(relative_path: str) -> str:
    this_file_path = os.path.dirname(os.path.abspath(__file__))
    if not relative_path.startswith("/"):
        relative_path = "/" + relative_path
    return this_file_path.replace("/src/utils", '') + relative_path
