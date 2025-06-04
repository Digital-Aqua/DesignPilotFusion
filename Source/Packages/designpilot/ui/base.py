from typing import Any, Generic, TypeVar

import rxprop as rx


class ViewModel(object):
    """ Base class for view models. """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    # @rx.value
    # def styling(self) -> rx.ReactiveList[str]:
    #     return rx.ReactiveList([self._default_class_style()])

    # @classmethod
    # @cache
    # def _default_class_style(cls) -> str:
    #     return snakecase(cls.__qualname__)


_T = TypeVar('_T')


class ViewModelRef(Generic[_T], ViewModel):
    """
    A view model containing a reference to a model.
    (The reference is not reactive.)
    """
    def __init__(self, model: _T, **kwargs: Any):
        super().__init__(**kwargs)
        self._model = model


_VM = TypeVar('_VM', bound=ViewModel)


class ContentVm(Generic[_VM], ViewModel):
    """ Mixin adding a content property to the view model. """
    @rx.value
    def content(self) -> rx.ReactiveList[_VM]:
        """
        A sequence of view models that comprise the content of this view model.
        """
        return rx.ReactiveList()
