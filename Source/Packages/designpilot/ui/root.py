from typing import Any

import rxprop as rx

from ..dpapp import DpApp
from .base import ViewModel
from .chat import ChatVm
from .basic import TextVm
from .settings import SettingsVm


class TabContainerVm(ViewModel):
    def __init__(self, *tabs: tuple[ViewModel, ViewModel], **kwargs: Any):
        super().__init__(**kwargs)
        self._tabs = tabs

    @rx.value
    def tabs(self) -> dict[ViewModel, ViewModel]:
        return dict(self._tabs)


class RootVm(ViewModel):
    def __init__(self, app: DpApp, **kwargs: Any):
        super().__init__(**kwargs)
        self._app = app

    @rx.value
    def chat(self) -> ChatVm:
        return ChatVm(self._app)

    @rx.value
    def settings(self) -> SettingsVm:
        return SettingsVm(self._app)

    @rx.value
    def tabs(self) -> TabContainerVm:
        return TabContainerVm(
            (TextVm('Chat'), self.chat),
            (TextVm('Settings'), self.settings),
        )
