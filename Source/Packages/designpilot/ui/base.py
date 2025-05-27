from functools import cache
from typing import Any, TypeVar

from caseconverter import snakecase

from rxprop import value


TValue = TypeVar("TValue")


class ViewModel(object):
    """ Base class for view models. """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    @value
    def styling(self) -> list[str]:
        return [self._default_class_style()]

    @classmethod
    @cache
    def _default_class_style(cls) -> str:
        return snakecase(cls.__qualname__)


class ContentVmMixin(ViewModel):
    """ Mixin adding a content property to the view model. """
    @value
    def content(self) -> list[ViewModel]:
        return []


class HeaderVmMixin(ViewModel):
    """ Mixin adding a header property to the view model. """
    @value
    def header(self) -> list[ViewModel]:
        return []


class FooterVmMixin(ViewModel):
    """ Mixin adding a footer property to the view model. """
    @value
    def footer(self) -> list[ViewModel]:
        return []
