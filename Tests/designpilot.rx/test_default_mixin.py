from designpilot.rx.typed_property import DefaultMixin, Getter
from typing import Any, Optional, Dict
from weakref import WeakKeyDictionary

class OwnerClass:
    _id_counter = 0
    def __init__(self):
        OwnerClass._id_counter += 1
        self.id = OwnerClass._id_counter

    @classmethod
    def reset_id_counter(cls):
        cls._id_counter = 0

class PropertyThatUsesDefault(DefaultMixin[OwnerClass, int]):
    def __init__(self, fdefault: Getter[OwnerClass, int], **kwargs: Any):
        super().__init__(fdefault=fdefault, **kwargs)
        self._values: WeakKeyDictionary[OwnerClass, int] = WeakKeyDictionary()
        self._is_set_flags: WeakKeyDictionary[OwnerClass, bool] = WeakKeyDictionary()

    def _get(self, instance: OwnerClass) -> int:
        if not self._is_set_flags.get(instance, False):
            return self.fdefault(instance)
        return self._values[instance]
    
    def _set_internal_value(self, owner_instance: OwnerClass, val: int) -> None:
        self._values[owner_instance] = val
        self._is_set_flags[owner_instance] = True

    def _clear_internal_value(self, owner_instance: OwnerClass) -> None:
        # Helper to reset state for an instance (for testing)
        if owner_instance in self._values:
            del self._values[owner_instance]
        if owner_instance in self._is_set_flags:
            del self._is_set_flags[owner_instance]

# This will be automatically picked up by pytest if present in the test file
def setup_function(_function: Any): # pytest will inject the test function here
    """Reset OwnerClass ID counter before each test."""
    OwnerClass.reset_id_counter()

def test_default_mixin_uses_fdefault_on_init():
    """Test DefaultMixin uses the provided fdefault (from init) when its _get is called by a subclass."""
    def default_factory(instance: OwnerClass) -> int:
        return 100 + instance.id

    prop = PropertyThatUsesDefault(fdefault=default_factory)
    prop.__set_name__(OwnerClass, "prop_default")

    instance1 = OwnerClass() # id will be 1 (due to setup_function)
    instance2 = OwnerClass() # id will be 2

    prop._clear_internal_value(instance1) # type: ignore[protected-access]
    prop._clear_internal_value(instance2) # type: ignore[protected-access]

    assert prop.__get__(instance1, OwnerClass) == 101
    assert prop.__get__(instance2, OwnerClass) == 102

def test_default_decorator_sets_fdefault():
    """Test default decorator method correctly sets/updates fdefault."""
    def initial_default(instance: OwnerClass) -> int:
        return 200 + instance.id

    prop = PropertyThatUsesDefault(fdefault=initial_default)
    prop.__set_name__(OwnerClass, "prop_default_deco")

    def new_default_factory(instance: OwnerClass) -> int:
        return 300 + instance.id

    returned_from_decorator = prop.default(new_default_factory)
    assert returned_from_decorator is prop 
    assert prop.fdefault is new_default_factory

    instance1 = OwnerClass() # id will be 1
    instance2 = OwnerClass() # id will be 2
    
    prop._clear_internal_value(instance1) # type: ignore[protected-access]
    assert prop.__get__(instance1, OwnerClass) == 301
    prop._clear_internal_value(instance2) # type: ignore[protected-access]
    assert prop.__get__(instance2, OwnerClass) == 302

def test_fdefault_called_with_instance():
    """Test fdefault is called with the instance as an argument."""
    # Using a dict to modify in nonlocal scope. Value can be OwnerClass or None.
    called_with_instance_holder: Dict[str, Optional[OwnerClass]] = {"instance": None}

    def my_default_factory(instance: OwnerClass) -> int:
        called_with_instance_holder["instance"] = instance
        return 42

    prop = PropertyThatUsesDefault(fdefault=my_default_factory)
    prop.__set_name__(OwnerClass, "prop_fdefault_arg")
    
    instance = OwnerClass() # id will be 1
    prop._clear_internal_value(instance) # type: ignore[protected-access]
    prop.__get__(instance, OwnerClass)
    
    assert called_with_instance_holder["instance"] is instance

def test_default_not_used_if_value_present_in_harness():
    """Test that PropertyThatUsesDefault does not use fdefault if a value is already set."""
    def default_factory(instance: OwnerClass) -> int:
        # This assertion will fail the test if this factory is unexpectedly called
        assert False, "Default factory should not be called when value is present"
        return 999 
    
    prop = PropertyThatUsesDefault(fdefault=default_factory)
    prop.__set_name__(OwnerClass, "prop_with_value")

    instance = OwnerClass() # id will be 1
    prop._set_internal_value(instance, 777) # type: ignore[protected-access]

    assert prop.__get__(instance, OwnerClass) == 777 