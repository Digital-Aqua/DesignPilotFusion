from functools import cache
from typing import AsyncIterator, Self, TypeVar

from caseconverter import snakecase

from ..rx import rx_value


TValue = TypeVar("TValue")


class ViewModel(object):
    """ Base class for view models. """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @rx_value
    def css_class(self) -> str:
        return ""

    @classmethod
    @cache
    def _default_css_class(cls) -> str:
        return snakecase(cls.__name__)


class HtmlElementVM(ViewModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
