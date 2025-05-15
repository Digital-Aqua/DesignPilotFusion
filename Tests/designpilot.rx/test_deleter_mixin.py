import pytest
from designpilot.rx.typed_property import DeleterMixin, TypedProperty
from typing import Any

class OwnerClass:
    _delete_flag: bool = False # To check if fdel was called
    _deleter_version_called: int = 0 # Class attribute for tracking deleter calls

class DeleterProperty(DeleterMixin[OwnerClass, Any]): # Value type is Any as delete doesn't use it
    pass

def test_deleter_mixin_with_fdel():
    """Test DeleterMixin allows deleting via a provided fdel function."""
    def del_value(instance: OwnerClass) -> None:
        instance._delete_flag = True # type: ignore

    prop = DeleterProperty(fdel=del_value)
    prop.__set_name__(OwnerClass, "prop_name")

    instance = OwnerClass()
    instance._delete_flag = False # type: ignore
    prop.__delete__(instance)
    assert instance._delete_flag is True # type: ignore

def test_deleter_decorator():
    """Test deleter decorator method correctly sets/updates fdel."""
    prop = DeleterProperty()
    prop.__set_name__(OwnerClass, "prop_name")

    # Reset class attribute for test
    OwnerClass._deleter_version_called = 0 # type: ignore

    def del_value_v1(instance: OwnerClass) -> None:
        OwnerClass._deleter_version_called = 1 # Modify class attribute # type: ignore

    returned_from_decorator = prop.deleter(del_value_v1)
    assert returned_from_decorator is prop # DeleterMixin.deleter returns self
    assert prop.fdel is del_value_v1
    
    instance = OwnerClass()
    OwnerClass._deleter_version_called = 0 # type: ignore
    prop.__delete__(instance)
    assert OwnerClass._deleter_version_called == 1 # type: ignore

    # Test updating fdel
    def del_value_v2(instance: OwnerClass) -> None:
        OwnerClass._deleter_version_called = 2 # Modify class attribute # type: ignore
    
    prop.deleter(del_value_v2)
    assert prop.fdel is del_value_v2
    OwnerClass._deleter_version_called = 0 # type: ignore
    prop.__delete__(instance)
    assert OwnerClass._deleter_version_called == 2 # type: ignore

def test_deleter_mixin_no_fdel_fallback():
    """Test _delete falls back to super()._delete if fdel is None."""
    prop = DeleterProperty() # fdel is None by default
    prop.__set_name__(OwnerClass, "prop_name")

    instance = OwnerClass()
    with pytest.raises(AttributeError, match="Property 'prop_name' does not support deleting a value."):
        prop.__delete__(instance)

class BaseDeleter(TypedProperty[OwnerClass, Any]):
    _custom_base_delete_called_for: Any = None
    def _delete(self, instance: OwnerClass) -> None:
        BaseDeleter._custom_base_delete_called_for = instance

class DeleterPropertyWithBase(DeleterMixin[OwnerClass, Any], BaseDeleter):
    pass

def test_deleter_mixin_no_fdel_fallback_to_custom_base():
    """Test _delete falls back to a custom super()._delete if fdel is None."""
    prop = DeleterPropertyWithBase() # fdel is None by default
    prop.__set_name__(OwnerClass, "prop_name")
    
    instance = OwnerClass()
    BaseDeleter._custom_base_delete_called_for = None # type: ignore
    prop.__delete__(instance)
    assert BaseDeleter._custom_base_delete_called_for is instance # type: ignore 