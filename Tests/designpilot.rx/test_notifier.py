import pytest
import asyncio
from unittest.mock import Mock
from designpilot.rx.events import Notifier

# Test Notifier Class

def test_notifier_add_handler_and_fire():
    notifier = Notifier()
    mock_handler = Mock()
    notifier.add_handler(mock_handler)
    notifier.fire()
    mock_handler.assert_called_once()

def test_notifier_add_same_handler_multiple_times_ref_counting():
    notifier = Notifier()
    mock_handler = Mock()
    notifier.add_handler(mock_handler)
    notifier.add_handler(mock_handler)
    notifier.fire()
    mock_handler.assert_called_once() # Still called once as fire iterates unique handlers
    notifier.remove_handler(mock_handler)
    notifier.fire()
    assert mock_handler.call_count == 2 # Called again
    notifier.remove_handler(mock_handler)
    notifier.fire()
    assert mock_handler.call_count == 2 # Not called anymore

def test_notifier_remove_handler():
    notifier = Notifier()
    mock_handler = Mock()
    notifier.add_handler(mock_handler)
    notifier.remove_handler(mock_handler)
    notifier.fire()
    mock_handler.assert_not_called()

def test_notifier_remove_handler_respects_ref_counting():
    notifier = Notifier()
    mock_handler_1 = Mock(name="handler1")
    mock_handler_2 = Mock(name="handler2")

    notifier.add_handler(mock_handler_1)
    notifier.add_handler(mock_handler_1) # Add first handler twice
    notifier.add_handler(mock_handler_2)

    notifier.fire()
    mock_handler_1.assert_called_once()
    mock_handler_2.assert_called_once()

    notifier.remove_handler(mock_handler_1)
    notifier.fire()
    assert mock_handler_1.call_count == 2 # Still called
    assert mock_handler_2.call_count == 2

    notifier.remove_handler(mock_handler_2)
    notifier.fire()
    assert mock_handler_1.call_count == 3 # Still called
    assert mock_handler_2.call_count == 2 # Not called anymore

    notifier.remove_handler(mock_handler_1)
    notifier.fire()
    assert mock_handler_1.call_count == 3 # Not called anymore
    assert mock_handler_2.call_count == 2


def test_notifier_fire_does_not_call_removed_handlers():
    notifier = Notifier()
    mock_handler_active = Mock()
    mock_handler_removed = Mock()

    notifier.add_handler(mock_handler_active)
    notifier.add_handler(mock_handler_removed)
    notifier.remove_handler(mock_handler_removed)

    notifier.fire()
    mock_handler_active.assert_called_once()
    mock_handler_removed.assert_not_called()

# Test Notifier.handler_context

def test_handler_context_handler_active_within_block():
    notifier = Notifier()
    mock_handler = Mock()
    with notifier.handler_context(mock_handler):
        notifier.fire()
    mock_handler.assert_called_once()

def test_handler_context_handler_inactive_after_block_normal_exit():
    notifier = Notifier()
    mock_handler = Mock()
    with notifier.handler_context(mock_handler):
        pass
    notifier.fire()
    mock_handler.assert_not_called()

def test_handler_context_handler_inactive_after_block_exception_exit():
    notifier = Notifier()
    mock_handler = Mock()
    with pytest.raises(ValueError):
        with notifier.handler_context(mock_handler):
            raise ValueError("Test exception")
    notifier.fire()
    mock_handler.assert_not_called()

# Test Notifier.event_context

@pytest.mark.asyncio
async def test_event_context_yields_event():
    notifier = Notifier()
    with notifier.event_context() as event:
        assert isinstance(event, asyncio.Event)

@pytest.mark.asyncio
async def test_event_context_event_set_on_fire():
    notifier = Notifier()
    with notifier.event_context() as event:
        assert not event.is_set()
        notifier.fire()
        await asyncio.wait_for(event.wait(), timeout=0.1)
        assert event.is_set()

@pytest.mark.asyncio
async def test_event_context_event_not_set_after_exit():
    notifier = Notifier()
    event_ref = None
    with notifier.event_context() as event:
        event_ref = event
    
    assert event_ref is not None
    notifier.fire()
    await asyncio.sleep(0.01) # give time for any potential set
    assert not event_ref.is_set()


@pytest.mark.asyncio
async def test_event_context_multiple_instances():
    notifier = Notifier()
    event1_fired = False
    event2_fired = False

    async def task1():
        nonlocal event1_fired
        with notifier.event_context() as event1:
            await event1.wait()
            event1_fired = True

    async def task2():
        nonlocal event2_fired
        with notifier.event_context() as event2:
            await event2.wait()
            event2_fired = True
            
    asyncio.create_task(task1())
    asyncio.create_task(task2())
    
    await asyncio.sleep(0.01) # allow tasks to start and enter context
    notifier.fire()
    await asyncio.sleep(0.01) # allow tasks to process event
    
    assert event1_fired
    assert event2_fired

# Note: Testing WeakKeyDictionary behavior for _handlers is difficult and often
# non-deterministic as it relies on garbage collection.
# We acknowledge its use and trust Python's GC mechanisms.
# If specific issues arise related to GC, targeted tests might be needed. 