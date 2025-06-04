from typing import Any

from ..dpapp import DpApp
from .base import ViewModel


class SettingsVm(ViewModel):
    def __init__(self, app: DpApp, **kwargs: Any):
        super().__init__(**kwargs)
        self._app = app
