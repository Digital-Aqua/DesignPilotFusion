import asyncio
from unittest.mock import MagicMock
from typing import Any, Optional, Callable, Type, Dict, Set as TypingSet
import weakref

from designpilot.rx.rx_computed import ComputedPropertyMixin, CachedPropertyMixin
from designpilot.rx.rx_property import ReactivePropertyMixin
from designpilot.rx.events import Notifier
from designpilot.rx.typed_property import TypedProperty, GetterMixin

class BaseProperty(TypedProperty[Any, Any]):
    _name: str

    def __init__(self, fref: Optional[Callable[..., Any]] = None):
        super().__init__()
        self.fref = fref
        
        self._values: Dict[Any, Any] = {}
        self._dirty: Dict[Any, asyncio.Event] = {}
        self._deps: weakref.WeakKeyDictionary[Any, TypingSet[Notifier]] = weakref.WeakKeyDictionary()
        self._notifiers: weakref.WeakKeyDictionary[Any, Notifier] = weakref.WeakKeyDictionary()

    def __set_name__(self, owner: Type[Any], name: str) -> None:
        self._name = name
        if self.fref is not None:
            if not hasattr(self, '__doc__') or self.__doc__ is None:
                self.__doc__ = getattr(self.fref, '__doc__', None)

    def _get(self, instance: Any) -> Any:
        raise AttributeError(f"'{type(instance).__name__}' object has no attribute '{self._name}'")

    def _set(self, instance: Any, value: Any) -> None:
        raise AttributeError(f"can't set attribute '{self._name}'")

    def _delete(self, instance: Any) -> None:
        raise AttributeError(f"can't delete attribute '{self._name}'")

    def _get_notifier(self, instance: Any) -> Notifier:
        if not hasattr(self, '_notifiers'):
            self._notifiers = weakref.WeakKeyDictionary()
            
        notifier = self._notifiers.get(instance)
        if notifier is None:
            notifier = Notifier()
            self._notifiers[instance] = notifier
        return notifier

# Helper class for creating controlled reactive dependencies in tests
class SimpleReactivePropertyHelper(ReactivePropertyMixin[Any, Any], GetterMixin[Any, Any], BaseProperty): # type: ignore[override]
    _value_store: Any
    _notifier_override: Optional[Notifier] = None 

    def __init__(self, initial_value: Any):
        super().__init__(fget=self._actual_get_val) # Provides fget to GetterMixin via **kwargs
        self._value_store = initial_value

    def _actual_get_val(self, instance: Any) -> Any: # The fget implementation
        return self._value_store

    def _get_notifier(self, instance: Any) -> Notifier: # Override for test control
        if self._notifier_override is not None:
            return self._notifier_override
        return super()._get_notifier(instance)

    # _get behavior is inherited:
    # SimpleReactivePropertyHelper -> ReactivePropertyMixin._get -> GetterMixin._get (calls fget) -> BaseProperty._get (if fget is None)
    # ReactivePropertyMixin._get handles dependency registration.
    # GetterMixin._get calls self.fget (our _actual_get_val) to retrieve the value.

class TestComputedPropertyMixin:
    def test_get_calls_fcompute(self) -> None:
        mock_fcompute: MagicMock = MagicMock(return_value="computed_value")

        class PropWithComputed(ComputedPropertyMixin[Any, Any], BaseProperty): # type: ignore[override]
            def __init__(self) -> None:
                super().__init__(fcompute=mock_fcompute)

        class Owner:
            prop: PropWithComputed = PropWithComputed()

        instance = Owner()
        val = instance.prop
        assert val == "computed_value"
        mock_fcompute.assert_called_once_with(instance)

    def test_dependency_tracking_no_initial_deps(self) -> None:
        dep_notifier = Notifier()
        dep_notifier.add_handler = MagicMock() # Mock to check if it's called

        # Create a reactive property that will act as the dependency
        # Its notifier is dep_notifier
        dependency_prop_descriptor = SimpleReactivePropertyHelper(initial_value="dependency_value")
        dependency_prop_descriptor._notifier_override = dep_notifier # type: ignore [protected-access]

        class DependencyOwner:
            source: SimpleReactivePropertyHelper = dependency_prop_descriptor
        
        dep_owner_instance = DependencyOwner()

        def compute_func(inst: Any) -> str:
            # Access the dependency property. This will trigger its _get method,
            # which in turn calls ReactivePropertyMixin._get, registering dep_notifier
            # with the listen_for_dependencies context (via the module-level _dep_ctx_stack).
            _ = dep_owner_instance.source 
            return "value_from_deps"

        computed_prop_notifier = Notifier()

        class PropWithComputedDeps(ComputedPropertyMixin[Any, Any], ReactivePropertyMixin[Any, Any], BaseProperty): # type: ignore[override]
            _owner_instance_for_mock_notifier: Optional[Any] = None
            _mock_notifier_for_instance: Optional[Notifier] = None

            def __init__(self, owner_instance_for_mock: Any, mock_notifier: Notifier) -> None:
                super().__init__(fcompute=compute_func) 
                self._owner_instance_for_mock_notifier = owner_instance_for_mock
                self._mock_notifier_for_instance = mock_notifier
            
            def _get_notifier(self, instance: Any) -> Notifier:
                if instance is self._owner_instance_for_mock_notifier:
                    assert self._mock_notifier_for_instance is not None
                    return self._mock_notifier_for_instance
                return super()._get_notifier(instance)

        class MainTestOwner:
            prop: Optional[PropWithComputedDeps] = None

        main_instance = MainTestOwner()
        prop_descriptor = PropWithComputedDeps(owner_instance_for_mock=main_instance, mock_notifier=computed_prop_notifier)
        MainTestOwner.prop = prop_descriptor
        prop_descriptor.__set_name__(MainTestOwner, 'computed_prop')

        val = main_instance.prop # type: ignore [union-attr]
        assert val == "value_from_deps"
        
        dep_notifier.add_handler.assert_called_once_with(computed_prop_notifier.fire)
        
        assert prop_descriptor._deps.get(main_instance) == {dep_notifier} # type: ignore [protected-access]

    def test_dependency_tracking_add_and_remove_deps(self) -> None:
        dep1_notifier = Notifier()
        dep1_notifier.add_handler = MagicMock(name="dep1_add_handler")
        dep1_notifier.remove_handler = MagicMock(name="dep1_remove_handler")

        dep2_notifier = Notifier()
        dep2_notifier.add_handler = MagicMock(name="dep2_add_handler")
        dep2_notifier.remove_handler = MagicMock(name="dep2_remove_handler")

        dep3_notifier = Notifier()
        dep3_notifier.add_handler = MagicMock(name="dep3_add_handler")
        dep3_notifier.remove_handler = MagicMock(name="dep3_remove_handler")

        # Create reactive properties for each notifier
        class DynamicDepOwner:
            # Attributes will be set after instance creation for clarity
            prop1: Optional[SimpleReactivePropertyHelper] = None
            prop2: Optional[SimpleReactivePropertyHelper] = None
            prop3: Optional[SimpleReactivePropertyHelper] = None

        # Property descriptors
        dep_prop1_desc = SimpleReactivePropertyHelper(initial_value="val1")
        dep_prop1_desc._notifier_override = dep1_notifier # type: ignore [protected-access]
        dep_prop2_desc = SimpleReactivePropertyHelper(initial_value="val2")
        dep_prop2_desc._notifier_override = dep2_notifier # type: ignore [protected-access]
        dep_prop3_desc = SimpleReactivePropertyHelper(initial_value="val3")
        dep_prop3_desc._notifier_override = dep3_notifier # type: ignore [protected-access]

        # Assign descriptors to the class
        DynamicDepOwner.prop1 = dep_prop1_desc
        DynamicDepOwner.prop2 = dep_prop2_desc
        DynamicDepOwner.prop3 = dep_prop3_desc
        
        # Instance that owns these dependency properties
        dynamic_dep_owner_inst = DynamicDepOwner()

        # Map notifiers to the actual property access on the owner instance
        # The lambda ensures the property is accessed on the instance when called
        deps_access_map: Dict[Notifier, Callable[[], Any]] = {
            dep1_notifier: lambda: dynamic_dep_owner_inst.prop1,
            dep2_notifier: lambda: dynamic_dep_owner_inst.prop2,
            dep3_notifier: lambda: dynamic_dep_owner_inst.prop3,
        }

        self.current_deps_to_trigger_access: TypingSet[Notifier] = set() # Renamed for clarity
        compute_calls_ref = [0]

        def get_compute_func_dynamic_deps() -> Callable[[Any], str]:
            test_method_self = self 
            def compute_func_dynamic_deps_inner(inst: Any) -> str:
                compute_calls_ref[0] += 1
                # Access the properties whose notifiers are in current_deps_to_trigger_access
                for notifier_key in test_method_self.current_deps_to_trigger_access:
                    if notifier_key in deps_access_map:
                        _ = deps_access_map[notifier_key]() # Access the property
                return f"computed_val_{compute_calls_ref[0]}"
            return compute_func_dynamic_deps_inner
        
        fcompute_method_for_prop = get_compute_func_dynamic_deps()
        prop_specific_notifier = Notifier()

        class PropWithDynamicDeps(ComputedPropertyMixin[Any, Any], ReactivePropertyMixin[Any, Any], BaseProperty): # type: ignore[override]
            _owner_instance_ref: Optional[Any] = None
            _specific_notifier_ref: Optional[Notifier] = None

            def __init__(self, fcompute_ext_method: Callable[[Any], str], owner_instance_ref: Any, specific_notifier: Notifier) -> None:
                super().__init__(fcompute=fcompute_ext_method)
                self._owner_instance_ref = owner_instance_ref
                self._specific_notifier_ref = specific_notifier
            
            def _get_notifier(self, instance: Any) -> Notifier:
                if instance is self._owner_instance_ref:
                    assert self._specific_notifier_ref is not None
                    return self._specific_notifier_ref
                return super()._get_notifier(instance)

        class Owner:
            prop: Optional[PropWithDynamicDeps] = None

        test_owner_instance = Owner()
        prop_instance = PropWithDynamicDeps(
            fcompute_ext_method=fcompute_method_for_prop,
            owner_instance_ref=test_owner_instance,
            specific_notifier=prop_specific_notifier 
        )
        Owner.prop = prop_instance
        prop_instance.__set_name__(Owner, "prop")

        compute_calls_ref[0] = 0
        self.current_deps_to_trigger_access = {dep1_notifier, dep2_notifier}

        val1 = prop_instance._get(test_owner_instance) # type: ignore [protected-access]
        assert val1 == "computed_val_1"
        assert prop_instance._deps.get(test_owner_instance) == {dep1_notifier, dep2_notifier} # type: ignore [protected-access]
        
        dep1_notifier.add_handler.assert_called_once_with(prop_specific_notifier.fire)
        dep2_notifier.add_handler.assert_called_once_with(prop_specific_notifier.fire)
        dep3_notifier.add_handler.assert_not_called()

        dep1_notifier.add_handler.reset_mock()
        dep2_notifier.add_handler.reset_mock()
        dep1_notifier.remove_handler.assert_not_called()
        dep2_notifier.remove_handler.assert_not_called()
        dep3_notifier.remove_handler.assert_not_called()

        compute_calls_ref[0] = 0
        self.current_deps_to_trigger_access = {dep2_notifier, dep3_notifier}
            
        val2 = prop_instance._get(test_owner_instance) # type: ignore [protected-access]
        assert val2 == "computed_val_1"
        assert prop_instance._deps.get(test_owner_instance) == {dep2_notifier, dep3_notifier} # type: ignore [protected-access]

        dep1_notifier.remove_handler.assert_called_once_with(prop_specific_notifier.fire)
        dep1_notifier.add_handler.assert_not_called()

        dep2_notifier.add_handler.assert_not_called()
        dep2_notifier.remove_handler.assert_not_called()

        dep3_notifier.add_handler.assert_called_once_with(prop_specific_notifier.fire)
        dep3_notifier.remove_handler.assert_not_called()
        
        dep1_notifier.remove_handler.reset_mock()
        dep2_notifier.add_handler.reset_mock()
        dep2_notifier.remove_handler.reset_mock()
        dep3_notifier.add_handler.reset_mock()

        compute_calls_ref[0] = 0
        self.current_deps_to_trigger_access = set()

        val3 = prop_instance._get(test_owner_instance) # type: ignore [protected-access]
        assert val3 == "computed_val_1" 
        assert prop_instance._deps.get(test_owner_instance) == set() # type: ignore [protected-access]

        dep1_notifier.remove_handler.assert_not_called()
        dep2_notifier.remove_handler.assert_called_once_with(prop_specific_notifier.fire)
        dep3_notifier.remove_handler.assert_called_once_with(prop_specific_notifier.fire)

    def test_weakkeydictionary_for_deps(self) -> None:
        mock_fcompute_wk: MagicMock = MagicMock(return_value="val")
        class Prop(ComputedPropertyMixin[Any,Any], BaseProperty): # type: ignore[override]
            def __init__(self) -> None:
                super().__init__(fcompute=mock_fcompute_wk)
        
        prop_instance_obj = Prop()
        assert isinstance(prop_instance_obj._deps, weakref.WeakKeyDictionary) # type: ignore [protected-access]

# CachedPropertyMixin import for later use, mark as used to satisfy linter for now
_ = CachedPropertyMixin
