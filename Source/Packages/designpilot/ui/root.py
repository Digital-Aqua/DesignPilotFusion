from typing import Any

import rxprop as rx

from ..dpapp import DpApp
from .base import ViewModel
from .basic import TextVm, ExpanderVm
from .chat import ChatVm
from .settings import SettingsVm



class RootVm(ViewModel):
    def __init__(self, app: DpApp, **kwargs: Any):
        super().__init__(**kwargs)
        self._app = app

    @rx.value
    def settings(self) -> ExpanderVm:
        return ExpanderVm(
            header = TextVm('Settings'),
            content = SettingsVm(self._app),
            expanded = True
        )
    
    @rx.value
    def chat(self) -> ChatVm:
        return ChatVm(self._app)


    # @rx.value
    # def tabs(self) -> TabContainerVm:
    #     return TabContainerVm(
    #         TabVm(TextVm('Chat'), self.chat),
    #         TabVm(TextVm('Settings'), self.settings),
    #     )
