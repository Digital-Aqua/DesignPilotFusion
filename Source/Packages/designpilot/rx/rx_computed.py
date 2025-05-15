import asyncio
from typing import Any, TypeVar
from weakref import WeakKeyDictionary

from .events import Notifier
from .rx_property import listen_for_dependencies, ReactivePropertyMixin
from .typed_property import Getter


_TClass = TypeVar("_TClass")
_TValue = TypeVar("_TValue")


class ComputedPropertyMixin(
    ReactivePropertyMixin[_TClass, _TValue]
):
    """
    A reactive property backed by a compute function.

    ReactiveProperties that are called within the compute function are
    automatically added as dependencies, triggering notification
    (and typically re-computation) when they change.
    """
    def __init__(self, fcompute: Getter[_TClass, _TValue], **kwargs: Any):
        super().__init__(**kwargs)
        self._fcompute = fcompute
        self._deps = WeakKeyDictionary[_TClass, set[Notifier]]()

    def _get(self, instance: _TClass) -> _TValue:
        old_deps = self._deps.get(instance, set[Notifier]())
        new_deps = set[Notifier]()

        # Recompute
        with listen_for_dependencies(new_deps):
            value = self._fcompute(instance)
        
        # Get the new dependencies and update accordingly
        instance_handler = self._get_notifier(instance).fire
        for dep in new_deps - old_deps:
            dep.add_handler(instance_handler)
        for dep in old_deps - new_deps:
            dep.remove_handler(instance_handler)
    
        # Save dependencies and return
        self._deps[instance] = new_deps
        return value


class CachedPropertyMixin(ReactivePropertyMixin[_TClass, _TValue]):
    """
    A reactive property with a cache and a dirty indicator.
    Prevents re-computation if the property is not dirty (very important!)
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._dirty = WeakKeyDictionary[_TClass, asyncio.Event]()
        self._values = WeakKeyDictionary[_TClass, _TValue]()

    def _is_dirty(self, instance: _TClass) -> bool:
        if not instance in self._dirty:
            event = asyncio.Event()
            event.set()
            notifier = self._get_notifier(instance)
            self._dirty[instance] = event
            notifier.add_handler(event.set)
        return (
            self._dirty[instance].is_set()
            or instance not in self._values
        )

    def _get(self, instance: _TClass) -> _TValue:
        # Bypass super() if cache is valid
        if not self._is_dirty(instance):
            return self._values[instance]
        # Recompute
        value = super()._get(instance)
        # Cache
        self._values[instance] = value
        self._dirty[instance].clear()
        return value


class ComputedProperty(
    CachedPropertyMixin[_TClass, _TValue],
    ComputedPropertyMixin[_TClass, _TValue]
):
    """
    A reactive property backed by a compute function.
    """


def rx_computed(
    fcompute: Getter[_TClass, _TValue]
) -> ComputedProperty[_TClass, _TValue]:
    """
    Decorator that creates a reactive property backed by a compute function.

    ReactiveProperties that are called within the compute function are
    automatically added as dependencies, triggering notification
    (and typically re-computation) when they change.
    """
    return ComputedProperty(fcompute=fcompute, fref=fcompute)
