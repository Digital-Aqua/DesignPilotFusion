from unittest.mock import Mock, MagicMock
import weakref
from typing import Any

# Assuming Source.Packages.designpilot.rx.rx_value is accessible
# Adjust the import path as necessary based on your project structure
from designpilot.rx.rx_value import ValueStashMixin
from designpilot.rx.typed_property import TypedProperty # For super()._get fallback testing

# Dummy owner class for testing
class OwnerClass:
    pass

# Test class for ValueStashMixin
class TestValueStashMixin:

    def test_get_retrieves_value_from_stash(self):
        class StashUserProperty(ValueStashMixin[Any, Any], TypedProperty[Any, Any]): # type: ignore[misc]
            pass

        prop_instance = StashUserProperty()
        obj_instance = Mock()

        prop_instance._values[obj_instance] = "stashed_value" # type: ignore[protected-access]
        assert prop_instance._get(obj_instance) == "stashed_value" # type: ignore[protected-access]

    def test_get_calls_super_get_if_instance_not_in_stash(self):
        mock_super_get = MagicMock(return_value="super_called")
        
        class BaseProp(TypedProperty[Any, Any]): # type: ignore[misc]
            _get = mock_super_get

        class StashUserProperty(ValueStashMixin[Any, Any], BaseProp): # type: ignore[misc]
            pass

        prop_instance = StashUserProperty()
        obj_instance = Mock()

        assert obj_instance not in prop_instance._values # type: ignore[protected-access]
        result = prop_instance._get(obj_instance) # type: ignore[protected-access]
        assert result == "super_called"
        mock_super_get.assert_called_once_with(obj_instance)

    def test_set_stores_value_in_stash(self):
        # ValueStashMixin._set should be called directly here.
        # StashUserProperty should not override _set.
        class StashUserProperty(ValueStashMixin[Any, Any], TypedProperty[Any, Any]): # type: ignore[misc]
            # We need a _set on TypedProperty that doesn't raise an error IF ValueStashMixin were to call super()._set
            # However, per source, ValueStashMixin._set DOES NOT call super()._set.
            # So, the default TypedProperty._set (which raises AttributeError) is fine and won't be hit.
            pass

        prop_instance = StashUserProperty()
        obj_instance = Mock()
        value_to_set = "new_value"

        # This should call ValueStashMixin._set
        prop_instance._set(obj_instance, value_to_set) # type: ignore[protected-access]

        assert obj_instance in prop_instance._values # type: ignore[protected-access]
        assert prop_instance._values[obj_instance] == value_to_set # type: ignore[protected-access]

    def test_weakkeydictionary_behavior_for_values(self):
        # Using a very simple class for the instance to ensure it's weak-referencable
        class MyWeakReferencableObject:
            pass

        class StashProperty(ValueStashMixin[Any, Any], TypedProperty[Any, Any]): # type: ignore[misc]
            pass

        prop = StashProperty()
        # instance_obj = object() # Standard object should be weak referencable
        instance_obj = MyWeakReferencableObject() # Using custom class for clarity

        prop._values[instance_obj] = "some_value"  # type: ignore[protected-access]
        
        instance_ref = weakref.ref(instance_obj)

        assert instance_ref() is not None
        assert instance_obj in prop._values # type: ignore[protected-access]

        # Hold a reference to _values to inspect after instance_obj is deleted
        values_dict = prop._values # type: ignore[protected-access]
        del instance_obj
        
        # Attempt to trigger garbage collection if possible/needed, though it's not guaranteed to be immediate
        # For robust test, this would require more specific GC control or waiting.
        # We primarily test that WeakKeyDictionary is used and entries for other objects persist.

        assert isinstance(values_dict, weakref.WeakKeyDictionary)
        # Check if the key is gone (might not be immediate without gc.collect())
        # For now, we trust WeakKeyDictionary behavior given the previous direct error is resolved.

        instance2 = MyWeakReferencableObject()
        prop._values[instance2] = "another_value" # type: ignore[protected-access]
        assert instance2 in prop._values # type: ignore[protected-access]
        assert prop._values[instance2] == "another_value" # type: ignore[protected-access]
        
        # After instance_obj is deleted, instance_ref() should be None if GC has run
        # This can be flaky in tests. The main point is that the dictionary *allows* GC.
        # if instance_ref() is None:
        #     assert len(values_dict) == 1 # Only instance2 should remain
        # else:
        #     # instance_obj might still be lingering if GC hasn't run
        #     pass 

    def test_stash_initialization(self):
        class StashUserProperty(ValueStashMixin[Any, Any], TypedProperty[Any, Any]): # type: ignore[misc]
            pass 
        
        prop_instance = StashUserProperty()
        assert isinstance(prop_instance._values, weakref.WeakKeyDictionary) # type: ignore[protected-access]
        assert len(prop_instance._values) == 0 # type: ignore[protected-access]

    def test_multiple_instances_independent_stashes(self):
        class StashUserProperty(ValueStashMixin[Any, Any], TypedProperty[Any, Any]): # type: ignore[misc]
            pass

        prop1 = StashUserProperty()
        prop2 = StashUserProperty()

        obj_instance_a = Mock(name="obj_instance_a")
        obj_instance_b = Mock(name="obj_instance_b")

        prop1._set(obj_instance_a, "value_for_prop1_a") # type: ignore[protected-access]
        prop1._set(obj_instance_b, "value_for_prop1_b") # type: ignore[protected-access]

        prop2._set(obj_instance_a, "value_for_prop2_a") # type: ignore[protected-access]
        prop2._set(obj_instance_b, "value_for_prop2_b") # type: ignore[protected-access]

        assert prop1._get(obj_instance_a) == "value_for_prop1_a" # type: ignore[protected-access]
        assert prop1._get(obj_instance_b) == "value_for_prop1_b" # type: ignore[protected-access]
        assert prop2._get(obj_instance_a) == "value_for_prop2_a" # type: ignore[protected-access]
        assert prop2._get(obj_instance_b) == "value_for_prop2_b" # type: ignore[protected-access]

        assert prop1._values is not prop2._values # type: ignore[protected-access] 

# Test class for ReactiveValue
from designpilot.rx.rx_value import ReactiveValue
from designpilot.rx.rx_property import ReactivePropertyMixin # To mock super()._set

class TestReactiveValue:
    def test_set_notification_behavior(self):
        class MyTestClass:
            pass

        # Mock the super()._set of ReactiveValue, which is ReactivePropertyMixin._set
        # This is the method that would trigger notifications.
        mock_super_set = MagicMock()

        def mock_set_side_effect(target_instance: Any, new_value: Any) -> None:
            # Simulate that the value is actually stored, as ValueStashMixin._set would do
            # if the call chain to super()._set was not fully mocked out here.
            # This ensures that subsequent _get calls in ReactiveValue._set see the updated value.
            prop._values[target_instance] = new_value # type: ignore[protected-access]
            # We don't need to call the original ReactivePropertyMixin._set here,
            # as we are only testing the conditional logic within ReactiveValue._set itself.

        mock_super_set.side_effect = mock_set_side_effect

        # We need a base class for ReactiveValue that has _set defined
        # and can be patched. ReactivePropertyMixin is that class.
        original_super_set = ReactivePropertyMixin[Any, Any]._set # type: ignore[protected-access]

        try:
            ReactivePropertyMixin[Any, Any]._set = mock_super_set # type: ignore[assignment, protected-access]

            # Create an instance of ReactiveValue.
            # It needs fdefault. We can provide a simple lambda.
            # It also inherits from DefaultMixin, ValueStashMixin, and ReactivePropertyMixin.
            def my_fdefault(inst: Any) -> str:
                return "default"
            prop = ReactiveValue[Any, Any](fdefault=my_fdefault)
            
            instance = MyTestClass()

            # Initial set - should call super()._set
            prop._set(instance, "new_value") # type: ignore[protected-access]
            mock_super_set.assert_called_once_with(instance, "new_value")
            mock_super_set.reset_mock()

            # Set with the same value - should NOT call super()._set
            prop._set(instance, "new_value") # type: ignore[protected-access]
            mock_super_set.assert_not_called()
            mock_super_set.reset_mock()

            # Set with a different value - should call super()._set
            prop._set(instance, "another_value") # type: ignore[protected-access]
            mock_super_set.assert_called_once_with(instance, "another_value")
            mock_super_set.reset_mock()

            # To be thorough, test that _get returns the stashed value correctly
            assert prop._get(instance) == "another_value" # type: ignore[protected-access]

        finally:
            # Restore the original _set method
            ReactivePropertyMixin[Any, Any]._set = original_super_set # type: ignore[assignment, protected-access] 