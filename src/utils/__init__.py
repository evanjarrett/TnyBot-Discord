import os

from .config import Config


def full_path(relative_path: str) -> str:
    return os.path.dirname(os.path.realpath(__file__)) + "/../../" + relative_path
