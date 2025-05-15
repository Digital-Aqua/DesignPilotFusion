import asyncio
from contextlib import contextmanager
from typing import Any, AsyncIterator, Iterator
from weakref import WeakKeyDictionary

from .events import Notifier
from .typed_property import (
    Getter, GetterMixin, SetterMixin, TypedProperty, TypeVar
)


_TClass = TypeVar("_TClass")
_TValue = TypeVar("_TValue")

_dep_ctx_stack: list[set[Notifier]] = []


@contextmanager
def listen_for_dependencies(buffer: set[Notifier]) -> Iterator[None]:
    """
    Context manager that listens for dependencies and adds them to `buffer`.
    Temporarily suppresses existing listeners until the context manager exits.
    """
    _dep_ctx_stack.append(buffer)
    try:
        yield
    finally:
        _dep_ctx_stack.pop()


class ReactivePropertyMixin(TypedProperty[_TClass, _TValue]):
    """
    A mixin for reactive properties.
    Provides `observe_async` for change notification,
    and reports usage of the property to dependency tracking.
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._notifiers = WeakKeyDictionary[_TClass, Notifier]()

    def _get_notifier(self, instance: _TClass) -> Notifier:
        """
        Returns a notifier for the given instance.
        If the notifier is not in the stash, a new notifier is created
        and added to the stash.
        """
        if not instance in self._notifiers:
            self._notifiers[instance] = Notifier()
        return self._notifiers[instance]

    def _get(self, instance: _TClass) -> _TValue:
        # Before getting, register us as a dependency (if anyone's listening)
        if _dep_ctx_stack:
            notifier = self._get_notifier(instance)
            _dep_ctx_stack[-1].add(notifier)
        return super()._get(instance)

    def _set(self, instance: _TClass, value: _TValue) -> None:
        # After setting, notify change
        super()._set(instance, value)
        self._get_notifier(instance).fire()

    async def watch_async(self, instance: _TClass) -> AsyncIterator[_TValue]:
        """
        Observes this property and yields new values when the property changes.

        NOT guaranteed to yield intermediate values if the property is set
        multiple times in quick succession.
        """
        notifier = self._get_notifier(instance)
        q = asyncio.Queue[_TValue](1) # Use a queue with specific type

        def _put_value_in_queue():
            try:
                # Try to put the current value; if queue is full, it means a value is pending processing
                q.put_nowait(self.__get__(instance, type(instance)))
            except asyncio.QueueFull:
                pass # A value is already queued, new one will be picked up on next cycle if still relevant

        notifier.add_handler(_put_value_in_queue)
        try:
            # Yield initial value immediately
            yield self.__get__(instance, type(instance))

            while True:
                try:
                    # Wait for a new value to be put in the queue by the notifier
                    value = await q.get()
                    yield value
                    q.task_done()
                except asyncio.CancelledError:
                    break # Exit loop if watcher task is cancelled
        finally:
            notifier.remove_handler(_put_value_in_queue)


class ReactiveProperty(
    ReactivePropertyMixin[_TClass, _TValue],
    GetterMixin[_TClass, _TValue],
    SetterMixin[_TClass, _TValue]
):
    """
    A reactive property backed by a getter and setter.
    """


def rx_property(
    fget: Getter[_TClass, _TValue]
) -> ReactiveProperty[_TClass, _TValue]:
    """
    Decorator that creates a reactive property backed by a getter function.
    Allows defining a setter using `@name.setter`.
    """
    # Ensure fref is passed for docstring and name, fget for the actual getter.
    return ReactiveProperty(fget=fget, fref=fget)
