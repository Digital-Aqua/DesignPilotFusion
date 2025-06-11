from typing import Any

import rxprop as rx

from .base import ViewModel, ViewModelRef


__all__ = [
    'TextVm'
]


class TextVm(ViewModel):
    def __init__(self, text: str = '', **kwargs: Any):
        super().__init__(**kwargs)
        self.text = text

    @rx.value
    def text(self) -> str:
        """ The plaintext content. """
        ...


class MarkdownVm(ViewModelRef[str]):
    @property
    def content(self) -> str:
        """ The content in markdown format. """
        return self._model


class ExpanderVm(ViewModel):
    def __init__(self,
        header: ViewModel,
        content: ViewModel,
        expanded: bool = False,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.header = header
        self.content = content
        self.expanded = expanded

    @rx.value
    def expanded(self) -> bool:
        """ Whether the expander is expanded. """
        ...

    @rx.value
    def header(self) -> ViewModel:
        """ The header of the expander. """
        ...

    @rx.value
    def content(self) -> ViewModel:
        """ The content of the expander. """
        ...

    def toggle(self, **_: Any) -> None:
        """ Toggle the expanded state. """
        self.expanded = not self.expanded
    
    def expand(self, **_: Any) -> None:
        """ Expand the expander. """
        self.expanded = True
    
    def collapse(self, **_: Any) -> None:
        """ Collapse the expander. """
        self.expanded = False
