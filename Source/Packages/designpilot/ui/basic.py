from typing import Any

import rxprop as rx

from .base import ContentVm, ViewModel


__all__ = [
    'TextVm',
    'ButtonVm',
]


class TextVm(ViewModel):
    def __init__(self, text: str = '', **kwargs: Any):
        super().__init__(**kwargs)
        self.text = text

    @rx.value
    def text(self) -> str:
        ...


class ButtonVm(ContentVm[ViewModel], ViewModel):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.on_click = rx.Notifier[None]()
