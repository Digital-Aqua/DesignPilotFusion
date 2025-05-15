import pytest
from designpilot.rx.typed_property import GetterMixin, TypedProperty

class OwnerClass:
    pass

class GetterProperty(GetterMixin[OwnerClass, int]):
    pass

def test_getter_mixin_with_fget():
    """Test GetterMixin allows getting a value via a provided fget function."""
    def get_value(instance: OwnerClass) -> int:
        return 42

    prop = GetterProperty(fget=get_value)
    prop.__set_name__(OwnerClass, "prop_name") # Simulate descriptor binding

    instance = OwnerClass()
    assert prop.__get__(instance, OwnerClass) == 42

def test_getter_decorator():
    """Test getter decorator method correctly sets/updates fget."""
    prop = GetterProperty()
    prop.__set_name__(OwnerClass, "prop_name")

    def get_value_v1(instance: OwnerClass) -> int:
        return 123
    
    # Call the getter method to set fget. 
    # The 'getter' method is designed to be used as a decorator or directly.
    # When used as prop.getter(func), it sets func as the getter and returns prop itself.
    returned_from_decorator = prop.getter(get_value_v1)
    
    assert returned_from_decorator is prop  # GetterMixin.getter returns self
    assert prop.fget is get_value_v1 # Check that fget was set to our function
    
    instance = OwnerClass()
    assert prop.__get__(instance, OwnerClass) == 123 # Check that the getter function works

    # Test updating fget by calling .getter() again
    def get_value_v2(instance: OwnerClass) -> int:
        return 456
    
    prop.getter(get_value_v2)
    assert prop.fget is get_value_v2 # Check fget was updated
    assert prop.__get__(instance, OwnerClass) == 456 # Check new getter works


def test_getter_mixin_no_fget_fallback():
    """Test _get falls back to super()._get if fget is None."""
    prop = GetterProperty() # fget is None by default
    prop.__set_name__(OwnerClass, "prop_name")

    instance = OwnerClass()
    with pytest.raises(AttributeError, match="Property 'prop_name' does not have a value."):
        prop.__get__(instance, OwnerClass)

class BaseGetter(TypedProperty[OwnerClass, int]):
    def _get(self, instance: OwnerClass) -> int:
        return 789

class GetterPropertyWithBase(GetterMixin[OwnerClass, int], BaseGetter):
    pass

def test_getter_mixin_no_fget_fallback_to_custom_base():
    """Test _get falls back to a custom super()._get if fget is None."""
    prop = GetterPropertyWithBase() # fget is None by default
    prop.__set_name__(OwnerClass, "prop_name")
    
    instance = OwnerClass()
    # Should call BaseGetter._get
    assert prop.__get__(instance, OwnerClass) == 789 