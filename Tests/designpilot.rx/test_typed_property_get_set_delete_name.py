import pytest
from typing import Any
from designpilot.rx.typed_property import TypedProperty

class OwnerClass:
    # No fref, docstring should be empty, name set by __set_name__
    prop_no_fref: TypedProperty['OwnerClass', int] = TypedProperty()

    def fref_func(self) -> str:
        """This is a docstring for fref_func."""
        return "from_fref"

    # With fref, docstring and name should be inherited
    prop_with_fref: TypedProperty['OwnerClass', str] = TypedProperty(fref=fref_func)

def test_typed_property_instantiation_and_name_doc():
    """
    Test basic instantiation (e.g., with and without `fref`).
    Test `__set_name__` correctly sets the `_name` attribute (e.g., from class assignment).
    Test `__doc__` is inherited from `fref.__doc__` if `fref` is provided.
    Test `_name` is initialized from `fref.__name__` if `fref` is provided.
    """
    assert OwnerClass.prop_no_fref._name == "prop_no_fref"  # type: ignore[attr-defined]
    assert OwnerClass.prop_no_fref.__doc__ == ""

    # After class creation and __set_name__ has run, _name should be the assigned attribute name.
    assert OwnerClass.prop_with_fref._name == "prop_with_fref"  # type: ignore[attr-defined]
    assert OwnerClass.prop_with_fref.__doc__ == "This is a docstring for fref_func."


def test_typed_property_get_descriptor_behavior():
    """
    Test `__get__` descriptor behavior:
        - Returns `self` when instance is `None`.
        - Calls `_get` for an instance, which by default raises `AttributeError`.
    """
    instance = OwnerClass()

    # Returns self when instance is None
    assert OwnerClass.prop_no_fref is OwnerClass.__dict__["prop_no_fref"]
    assert OwnerClass.prop_with_fref is OwnerClass.__dict__["prop_with_fref"]

    # Calls _get for an instance, which by default raises AttributeError
    with pytest.raises(AttributeError, match="Property 'prop_no_fref' does not have a value."):
        _ = instance.prop_no_fref

    with pytest.raises(AttributeError, match="Property 'prop_with_fref' does not have a value."):
        _ = instance.prop_with_fref

def test_typed_property_set_descriptor_behavior():
    """
    Test `__set__` descriptor behavior:
        - Calls `_set`, which by default raises `AttributeError`.
    """
    instance = OwnerClass()
    with pytest.raises(AttributeError, match="Property 'prop_no_fref' does not support setting a value."):
        instance.prop_no_fref = 10

    with pytest.raises(AttributeError, match="Property 'prop_with_fref' does not support setting a value."):
        instance.prop_with_fref = "new_value"

def test_typed_property_delete_descriptor_behavior():
    """
    Test `__delete__` descriptor behavior:
        - Calls `_delete`, which by default raises `AttributeError`.
    """
    instance = OwnerClass()
    with pytest.raises(AttributeError, match="Property 'prop_no_fref' does not support deleting a value."):
        del instance.prop_no_fref

    with pytest.raises(AttributeError, match="Property 'prop_with_fref' does not support deleting a value."):
        del instance.prop_with_fref

class CustomProp(TypedProperty[Any, int]):
    def _get(self, instance: Any) -> int:
        return getattr(instance, f"_{self._name}_val", 0)  # type: ignore[attr-defined]

    def _set(self, instance: Any, value: int) -> None:
        setattr(instance, f"_{self._name}_val", value)  # type: ignore[attr-defined]

    def _delete(self, instance: Any) -> None:
        # Ensure _name is accessed correctly for the check
        name_val_attr = f"_{self._name}_val"  # type: ignore[attr-defined]
        if hasattr(instance, name_val_attr):
            delattr(instance, name_val_attr)
        else:
            # For testing, raise if already deleted or not set
            raise AttributeError(f"'{self._name}' was not set to delete.")  # type: ignore[attr-defined]


class OwnerWithCustomProp:
    custom_prop: CustomProp = CustomProp()

def test_typed_property_override_get_set_delete():
    """
    Test that _get, _set, _delete can be overridden and work.
    """
    instance = OwnerWithCustomProp()

    # Test default _get (simulated by not setting yet)
    assert instance.custom_prop == 0  # Default from custom _get

    # Test _set
    instance.custom_prop = 42
    assert instance.custom_prop == 42
    assert instance._custom_prop_val == 42  # type: ignore[attr-defined]

    # Test _delete
    del instance.custom_prop
    assert not hasattr(instance, "_custom_prop_val")  # type: ignore[attr-defined]

    # Test _get after delete (should be default again or error depending on _get impl)
    assert instance.custom_prop == 0  # Our custom _get returns 0

    # Test deleting again (should raise error based on our custom _delete)
    with pytest.raises(AttributeError, match="'custom_prop' was not set to delete."):
        del instance.custom_prop

# Test for __set_name__ explicitly
class AnotherOwner:
    explicit_prop: TypedProperty['AnotherOwner', float] = TypedProperty()

def test_set_name_explicitly():
    """Test __set_name__ correctly sets the _name attribute."""
    assert AnotherOwner.explicit_prop._name == "explicit_prop"  # type: ignore[attr-defined]
    # Try to access it on an instance to ensure it's working
    instance = AnotherOwner()
    with pytest.raises(AttributeError, match="Property 'explicit_prop' does not have a value."):
        _ = instance.explicit_prop

def fref_for_init_name() -> int:
    """Doc for init name."""
    return 1

class OwnerWithFrefInitName:
    prop: TypedProperty['OwnerWithFrefInitName', int] = TypedProperty(fref=fref_for_init_name)

def test_name_initialized_from_fref():
    """Test _name is initialized from fref.__name__ if fref is provided and __set_name__ hasn't overridden it yet."""
    # Accessing through the class __dict__ gets the descriptor before __set_name__ is called by class creation
    # For TypedProperty, the __init__ sets _name from fref if present.
    # Then __set_name__ (called by metaclass) overrides it with the assigned attribute name.
    
    # Check initial state from fref (this is tricky as __set_name__ runs early)
    # We can instantiate TypedProperty directly to check its __init__ behavior with fref
    prop_direct_fref = TypedProperty[Any, int](fref=fref_for_init_name)
    assert prop_direct_fref._name == "fref_for_init_name"  # type: ignore[attr-defined]
    assert prop_direct_fref.__doc__ == "Doc for init name."

    # After class assignment, __set_name__ should have updated it
    assert OwnerWithFrefInitName.prop._name == "prop"  # type: ignore[attr-defined]
    assert OwnerWithFrefInitName.prop.__doc__ == "Doc for init name."

class OwnerNoFref:
    prop: TypedProperty['OwnerNoFref', str] = TypedProperty()

def test_name_and_doc_without_fref():
    """Test _name and __doc__ when fref is not provided."""
    prop_direct_no_fref = TypedProperty[Any, str]()
    assert prop_direct_no_fref._name == ""  # type: ignore[attr-defined]
    assert prop_direct_no_fref.__doc__ == ""

    # After class assignment and __set_name__
    assert OwnerNoFref.prop._name == "prop"  # type: ignore[attr-defined]
    assert OwnerNoFref.prop.__doc__ == ""  # __doc__ remains empty as no fref 