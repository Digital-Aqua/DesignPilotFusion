import pytest
from unittest.mock import MagicMock, patch
from typing import Any

from designpilot.rx.rx_property import ReactivePropertyMixin, listen_for_dependencies, _dep_ctx_stack # type: ignore
from designpilot.rx.events import Notifier
from designpilot.rx.typed_property import TypedProperty

class MockOwner:
    pass

class TestListenForDependencies:
    def test_listen_adds_to_buffer(self):
        prop: ReactivePropertyMixin[Any, Any] = ReactivePropertyMixin()
        instance = MockOwner()
        
        mock_notifier = Notifier()
        prop._get_notifier = MagicMock(return_value=mock_notifier) # type: ignore

        buffer: set[Notifier] = set()
        assert len(_dep_ctx_stack) == 0

        with patch.object(TypedProperty, '_get', return_value="mocked_super_value") as mock_typed_property_get:
            with listen_for_dependencies(buffer):
                assert len(_dep_ctx_stack) == 1
                assert _dep_ctx_stack[0] is buffer
                prop.__get__(instance, MockOwner)

        assert len(_dep_ctx_stack) == 0
        assert len(buffer) == 1, f"Buffer has {len(buffer)} items, expected 1. Buffer: {buffer}"
        assert mock_notifier in buffer
        prop._get_notifier.assert_called_once_with(instance) # type: ignore
        mock_typed_property_get.assert_called_once_with(instance)

    def test_listen_stack_management(self):
        """Test _dep_ctx_stack is correctly managed (pushed on enter, popped on exit)."""
        buffer1: set[Notifier] = set()
        
        assert len(_dep_ctx_stack) == 0
        with listen_for_dependencies(buffer1):
            assert len(_dep_ctx_stack) == 1
            assert _dep_ctx_stack[0] is buffer1
            
            buffer2: set[Notifier] = set()
            with listen_for_dependencies(buffer2):
                assert len(_dep_ctx_stack) == 2
                assert _dep_ctx_stack[0] is buffer1
                assert _dep_ctx_stack[1] is buffer2
            
            assert len(_dep_ctx_stack) == 1
            assert _dep_ctx_stack[0] is buffer1
            
        assert len(_dep_ctx_stack) == 0

    def test_listen_stack_management_with_exception(self):
        """Test _dep_ctx_stack is correctly managed even with an exception."""
        buffer: set[Notifier] = set()
        
        assert len(_dep_ctx_stack) == 0
        with pytest.raises(ValueError):
            with listen_for_dependencies(buffer):
                assert len(_dep_ctx_stack) == 1
                assert _dep_ctx_stack[0] is buffer
                raise ValueError("Test exception")
        
        assert len(_dep_ctx_stack) == 0

    def test_listen_nested_contexts_dependencies_go_to_innermost(self):
        prop1: ReactivePropertyMixin[Any, Any] = ReactivePropertyMixin()
        prop2: ReactivePropertyMixin[Any, Any] = ReactivePropertyMixin()
        instance = MockOwner()

        notifier1 = Notifier()
        notifier2 = Notifier()
        prop1._get_notifier = MagicMock(return_value=notifier1) # type: ignore
        prop2._get_notifier = MagicMock(return_value=notifier2) # type: ignore

        outer_buffer: set[Notifier] = set()
        inner_buffer: set[Notifier] = set()

        with patch.object(TypedProperty, '_get', MagicMock(return_value="val1")) as mock_tp_get1:
            with listen_for_dependencies(outer_buffer):
                prop1.__get__(instance, MockOwner)

                with patch.object(TypedProperty, '_get', MagicMock(return_value="val2")) as mock_tp_get2:
                    with listen_for_dependencies(inner_buffer):
                        prop2.__get__(instance, MockOwner)
                    mock_tp_get2.assert_called_once_with(instance)
            
            mock_tp_get1.assert_called_once_with(instance)

        assert notifier2 not in outer_buffer
        assert notifier2 in inner_buffer, f"Notifier2 not in inner_buffer. Inner: {inner_buffer}"
        assert len(inner_buffer) == 1

        assert notifier1 in outer_buffer, f"Notifier1 not in outer_buffer. Outer: {outer_buffer}"
        assert len(outer_buffer) == 1
        assert notifier1 not in inner_buffer
        
        prop1._get_notifier.assert_called_once_with(instance) # type: ignore
        prop2._get_notifier.assert_called_once_with(instance) # type: ignore 