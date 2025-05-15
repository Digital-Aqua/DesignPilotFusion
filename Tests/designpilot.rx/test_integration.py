import asyncio
import pytest
from typing import List

from designpilot.rx import rx_value, rx_property, rx_computed

@pytest.mark.asyncio
class TestIntegration:
    async def test_value_prop_computed_interaction(self):
        """
        Tests that rx_value, rx_property, and rx_computed interact correctly.
        - rx_computed depends on an rx_value and an rx_property.
        - Changes in rx_value and rx_property trigger re-computation of rx_computed.
        """
        class MyClass:
            def __init__(self):
                self._multiplier = 2

            @rx_value
            def val_a(self) -> int:
                return 10

            @rx_property
            def prop_b(self) -> int: # type: ignore
                return self.val_a * self._multiplier

            @prop_b.setter
            def prop_b(self, value: int):
                # This setter allows prop_b to be set.
                # For this test, we'll set val_a based on this, assuming a fixed multiplier.
                if self._multiplier == 0: # Avoid division by zero
                    self.val_a = 0
                else:
                    self.val_a = value // self._multiplier

            @rx_computed
            def computed_c(self) -> int:
                return self.val_a + self.prop_b

        instance = MyClass()

        # Initial checks
        assert instance.val_a == 10
        assert instance.prop_b == 20  # 10 * 2
        assert instance.computed_c == 30 # 10 + 20

        # Watch computed_c for changes
        changes: List[int] = []
        async def watcher():
            async for value in MyClass.computed_c.watch_async(instance): # type: ignore
                changes.append(value)
        
        watcher_task = asyncio.create_task(watcher())
        # Allow watcher to consume initial value and start listening
        await asyncio.sleep(0) 
        assert changes == [30]

        # Change rx_value (val_a)
        instance.val_a = 5
        await asyncio.sleep(0) # allow propagation
        assert instance.val_a == 5
        assert instance.prop_b == 10 # 5 * 2
        assert instance.computed_c == 15 # 5 + 10
        # The watcher should pick up the new value of computed_c
        await asyncio.sleep(0) # ensure watcher task runs
        assert changes == [30, 15]

        # Change rx_property (prop_b) via its setter, which in turn changes val_a
        instance.prop_b = 30 # This will set val_a to 30 // 2 = 15
        await asyncio.sleep(0) # allow propagation
        assert instance.val_a == 15
        assert instance.prop_b == 30 # 15 * 2 (prop_b recomputes based on new val_a)
        assert instance.computed_c == 45 # 15 + 30
        await asyncio.sleep(0) # ensure watcher task runs
        assert changes == [30, 15, 45]

        # Test direct change to multiplier (internal state), affecting prop_b and computed_c
        instance._multiplier = 3 # type: ignore
        # We need to trigger a re-evaluation.
        # Setting val_a again (even to the same value) will trigger its observers,
        # which includes prop_b, and subsequently computed_c.
        current_val_a = instance.val_a # currently 15
        # instance.val_a = current_val_a # Re-set to trigger chain <-- This no longer works as expected
        # Force a change in val_a to trigger the reactive chain
        if instance.val_a == current_val_a: # Check if it's actually the same
            instance.val_a = current_val_a + 1 # Change it to something different
            await asyncio.sleep(0) # allow propagation for this intermediate change
            instance.val_a = current_val_a    # And then change it back to trigger re-computation

        await asyncio.sleep(0) # allow propagation for val_a's change (to current_val_a)
        await asyncio.sleep(0) # allow propagation for prop_b's change due to val_a and new multiplier
        await asyncio.sleep(0) # allow propagation for computed_c's change
        
        assert instance.val_a == 15
        # prop_b should now use the new multiplier
        assert instance.prop_b == 45 # 15 * 3
        assert instance.computed_c == 60 # 15 + 45
        await asyncio.sleep(0) # ensure watcher task runs for the value 64
        await asyncio.sleep(0) # ensure watcher task runs for the final value 60
        assert changes == [30, 15, 45, 64, 60]

        watcher_task.cancel()
        try:
            await watcher_task
        except asyncio.CancelledError:
            pass
