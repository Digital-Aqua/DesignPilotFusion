from typing import Any

from ..dpapp import DpApp
from .base import ContentVmMixin, HeaderVmMixin, FooterVmMixin, ViewModel


class DpVM(
    HeaderVmMixin,
    ContentVmMixin,
    FooterVmMixin,
    ViewModel
):
    def __init__(self, app: DpApp, **kwargs: Any):
        super().__init__(**kwargs)
        self._app = app

        self._chat = ChatVM(self._app)
        self._settings = SettingsVM(self._app)

        self.content = [
            self._chat,
            self._settings,
        ]
