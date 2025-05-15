import pytest
from designpilot.rx.typed_property import SetterMixin, TypedProperty
from typing import Any

class OwnerClass:
    _value_holder: Any = None # To store the value for testing fset

class SetterProperty(SetterMixin[OwnerClass, int]):
    pass

def test_setter_mixin_with_fset():
    """Test SetterMixin allows setting a value via a provided fset function."""
    def set_value(instance: OwnerClass, value: int) -> None:
        instance._value_holder = value # type: ignore

    prop = SetterProperty(fset=set_value)
    prop.__set_name__(OwnerClass, "prop_name") # Simulate descriptor binding

    instance = OwnerClass()
    prop.__set__(instance, 100)
    assert instance._value_holder == 100 # type: ignore

def test_setter_decorator():
    """Test setter decorator method correctly sets/updates fset."""
    prop = SetterProperty()
    prop.__set_name__(OwnerClass, "prop_name")

    def set_value_v1(instance: OwnerClass, value: int) -> None:
        instance._value_holder = value + 1 # v1 adds 1 # type: ignore

    returned_from_decorator = prop.setter(set_value_v1)
    assert returned_from_decorator is prop # SetterMixin.setter returns self
    assert prop.fset is set_value_v1
    
    instance = OwnerClass()
    prop.__set__(instance, 200)
    assert instance._value_holder == 201 # type: ignore

    # Test updating fset
    def set_value_v2(instance: OwnerClass, value: int) -> None:
        instance._value_holder = value + 2 # v2 adds 2 # type: ignore
    
    prop.setter(set_value_v2)
    assert prop.fset is set_value_v2
    prop.__set__(instance, 300)
    assert instance._value_holder == 302 # type: ignore

def test_setter_mixin_no_fset_fallback():
    """Test _set falls back to super()._set if fset is None."""
    prop = SetterProperty() # fset is None by default
    prop.__set_name__(OwnerClass, "prop_name")

    instance = OwnerClass()
    with pytest.raises(AttributeError, match="Property 'prop_name' does not support setting a value."):
        prop.__set__(instance, 400)

class BaseSetter(TypedProperty[OwnerClass, int]):
    _custom_base_set_called_with: Any = None
    def _set(self, instance: OwnerClass, value: int) -> None:
        # Store the value in a class attribute for simplicity in testing
        BaseSetter._custom_base_set_called_with = (instance, value)

class SetterPropertyWithBase(SetterMixin[OwnerClass, int], BaseSetter):
    pass

def test_setter_mixin_no_fset_fallback_to_custom_base():
    """Test _set falls back to a custom super()._set if fset is None."""
    prop = SetterPropertyWithBase() # fset is None by default
    prop.__set_name__(OwnerClass, "prop_name")
    
    instance = OwnerClass()
    BaseSetter._custom_base_set_called_with = None # Reset for clarity # type: ignore
    prop.__set__(instance, 500)
    assert BaseSetter._custom_base_set_called_with == (instance, 500) # type: ignore 