from typing import Any

from rxprop import Notifier, value

from .base import ContentVmMixin, ViewModel


__all__ = [
    'TextVM',
    'ButtonVM',
]


class TextVM(ViewModel):
    @value
    def text(self) -> str:
        return ''

class ButtonVM(ContentVmMixin, ViewModel):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.on_click = Notifier[None]()
