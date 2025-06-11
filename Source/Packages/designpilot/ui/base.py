from typing import Any, Generic, TypeVar

import rxprop as rx


_T = TypeVar('_T')


class ViewModel(object):
    """ Base class for view models. """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)


class EmptyVm(ViewModel): pass
empty_vm = EmptyVm()


class ViewModelRef(Generic[_T], ViewModel):
    """
    A view model containing a reference to a model.
    (The reference is not reactive.)
    """
    def __init__(self, model: _T, **kwargs: Any):
        super().__init__(**kwargs)
        self._model = model
        """ The model on which this view model depends. """


_VM = TypeVar('_VM', bound=ViewModel)


class ContentVm(Generic[_VM], ViewModel):
    """ Mixin adding a content property to the view model. """
    @rx.value
    def content(self) -> rx.ReactiveList[_VM]:
        """
        A sequence of view models that comprise the content of this view model.
        """
        return rx.ReactiveList()
