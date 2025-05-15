from typing import Any, TypeVar
from weakref import WeakKeyDictionary
from .rx_property import ReactivePropertyMixin
from .typed_property import DefaultMixin, Getter, TypedProperty


_TClass = TypeVar("_TClass")
_TValue = TypeVar("_TValue")


class ValueStashMixin(TypedProperty[_TClass, _TValue]):
    """
    Adds a stash of values to a `TypedProperty`.
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._values = WeakKeyDictionary[_TClass, _TValue]()

    def _get(self, instance: _TClass) -> _TValue:
        if instance in self._values:
            return self._values[instance]
        value = super()._get(instance)
        self._values[instance] = value
        return value
    
    def _set(self, instance: _TClass, value: _TValue) -> None:
        self._values[instance] = value


class ReactiveValue(
    ReactivePropertyMixin[_TClass, _TValue], # reactive logic
    ValueStashMixin[_TClass, _TValue],       # value storage logic
    DefaultMixin[_TClass, _TValue]           # fallback
):
    """
    A reactive property backed by a field.
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def _set(self, instance: _TClass, value: _TValue) -> None:
        # Skip updates (and thus notifications) if the value is the same
        old_value = self._get(instance)
        if old_value != value:
            super()._set(instance, value) # triggers notifier


def rx_value(fdefault: Getter[_TClass, _TValue]) -> ReactiveValue[_TClass, _TValue]:
    """
    Decorator that creates a reactive property backed by a field.
    The decorated function is called (lazily) to generate the default value.
    """
    return ReactiveValue(fdefault=fdefault, fref=fdefault)
