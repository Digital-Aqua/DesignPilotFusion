from functools import cache
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from types import ModuleType


class ResourceProvider:
    def __init__(self, root: Traversable|ModuleType):
        if isinstance(root, ModuleType):
            root = resources.files(root)
        self._root = root

    @cache
    def read_text(self, path: str|Path) -> str:
        path = Path(path)
        return (
            self._root
                .joinpath(*path.parts)
                .read_text()
        )
